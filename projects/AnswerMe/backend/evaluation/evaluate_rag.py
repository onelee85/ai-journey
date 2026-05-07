"""Run deterministic evaluations for the AnswerMe RAG application.

The workflow is:
1. Load a JSONL dataset with questions and expected answers/sources.
2. Run each question through the RAG app, either via HTTP API or service code.
3. Score answer relevance, answer accuracy, and retrieval quality.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
from urllib import request
from urllib.error import HTTPError, URLError


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT_DIR / "backend" / "evaluation" / "sample_dataset.jsonl"


@dataclass
class EvalCase:
    id: str
    question: str
    expected_answer: str = ""
    expected_sources: Optional[List[str]] = None
    expected_source_ids: Optional[List[str]] = None
    must_include: Optional[List[str]] = None
    must_not_include: Optional[List[str]] = None
    knowledge_base_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    top_k: Optional[int] = None


def load_dataset(path: Path) -> List[EvalCase]:
    cases: List[EvalCase] = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc

            cases.append(
                EvalCase(
                    id=str(item.get("id") or f"case_{line_number}"),
                    question=item["question"],
                    expected_answer=item.get("expected_answer", ""),
                    expected_sources=item.get("expected_sources"),
                    expected_source_ids=item.get("expected_source_ids"),
                    must_include=item.get("must_include"),
                    must_not_include=item.get("must_not_include"),
                    knowledge_base_id=item.get("knowledge_base_id"),
                    history=item.get("history", []),
                    top_k=item.get("top_k"),
                )
            )
    return cases


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def text_units(text: str) -> Set[str]:
    """Tokenize mixed Chinese/English text without third-party dependencies."""
    text = normalize_text(text)
    units: Set[str] = set(re.findall(r"[a-z0-9]+", text))
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    units.update(chinese_chars)
    units.update(
        "".join(chinese_chars[index : index + 2])
        for index in range(len(chinese_chars) - 1)
    )
    return {unit for unit in units if unit}


def f1_score(predicted: Iterable[str], expected: Iterable[str]) -> float:
    predicted_set = set(predicted)
    expected_set = set(expected)
    if not predicted_set or not expected_set:
        return 0.0
    overlap = len(predicted_set & expected_set)
    if overlap == 0:
        return 0.0
    precision = overlap / len(predicted_set)
    recall = overlap / len(expected_set)
    return 2 * precision * recall / (precision + recall)


def contains_all(text: str, phrases: Sequence[str]) -> bool:
    normalized = normalize_text(text)
    return all(normalize_text(phrase) in normalized for phrase in phrases)


def contains_any(text: str, phrases: Sequence[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(phrase) in normalized for phrase in phrases)


def source_values(source: Dict[str, Any]) -> Set[str]:
    metadata = source.get("metadata") or {}
    values = {
        str(source.get("document_id", "")),
        str(metadata.get("document_id", "")),
        str(metadata.get("filename", "")),
        str(metadata.get("file_path", "")),
    }
    return {normalize_text(value) for value in values if value}


def source_matches(source: Dict[str, Any], expected: str) -> bool:
    expected_normalized = normalize_text(expected)
    return any(
        expected_normalized == value or expected_normalized in value
        for value in source_values(source)
    )


def evaluate_case(case: EvalCase, result: Dict[str, Any]) -> Dict[str, Any]:
    answer = result.get("answer", "")
    sources = result.get("sources", [])

    expected_answer_score = (
        f1_score(text_units(answer), text_units(case.expected_answer))
        if case.expected_answer
        else 0.0
    )
    must_include_score = (
        1.0 if contains_all(answer, case.must_include or []) else 0.0
    )
    must_not_include_score = (
        0.0 if contains_any(answer, case.must_not_include or []) else 1.0
    )

    if case.expected_answer and case.must_include:
        answer_accuracy = (
            expected_answer_score * 0.60
            + must_include_score * 0.30
            + must_not_include_score * 0.10
        )
    elif case.expected_answer:
        answer_accuracy = expected_answer_score * 0.90 + must_not_include_score * 0.10
    elif case.must_include:
        answer_accuracy = must_include_score * 0.80 + must_not_include_score * 0.20
    else:
        answer_accuracy = must_not_include_score

    answer_relevance = f1_score(text_units(answer), text_units(case.question))

    expected_source_labels = case.expected_sources or []
    expected_source_ids = case.expected_source_ids or []
    expected_sources = [*expected_source_labels, *expected_source_ids]
    retrieval_hits = sum(
        1 for expected in expected_sources if any(source_matches(src, expected) for src in sources)
    )
    retrieval_recall = (
        retrieval_hits / len(expected_sources) if expected_sources else 1.0
    )

    relevant_sources = [
        src
        for src in sources
        if expected_sources and any(source_matches(src, expected) for expected in expected_sources)
    ]
    retrieval_precision = (
        len(relevant_sources) / len(sources)
        if expected_sources and sources
        else (1.0 if not expected_sources else 0.0)
    )
    retrieval_quality = (
        0.7 * retrieval_recall + 0.3 * retrieval_precision
        if expected_sources
        else retrieval_recall
    )

    overall = (
        answer_relevance * 0.25
        + answer_accuracy * 0.45
        + retrieval_quality * 0.30
    )

    return {
        "id": case.id,
        "question": case.question,
        "answer": answer,
        "sources": sources,
        "scores": {
            "answer_relevance": round(answer_relevance, 4),
            "answer_accuracy": round(answer_accuracy, 4),
            "retrieval_quality": round(retrieval_quality, 4),
            "retrieval_recall": round(retrieval_recall, 4),
            "retrieval_precision": round(retrieval_precision, 4),
            "overall": round(overall, 4),
        },
        "checks": {
            "must_include_passed": bool(must_include_score),
            "must_not_include_passed": bool(must_not_include_score),
            "retrieval_hits": retrieval_hits,
            "expected_source_count": len(expected_sources),
        },
    }


class RagRunner:
    def query(self, case: EvalCase, knowledge_base_id: str, top_k: int) -> Dict[str, Any]:
        raise NotImplementedError


class HttpRagRunner(RagRunner):
    def __init__(self, api_base: str):
        self.api_base = api_base.rstrip("/")

    def query(self, case: EvalCase, knowledge_base_id: str, top_k: int) -> Dict[str, Any]:
        payload = {
            "question": case.question,
            "knowledge_base_id": knowledge_base_id,
            "history": case.history or [],
            "temperature": 0,
            "top_k": case.top_k or top_k,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.api_base}/api/v1/chat/query",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach API at {self.api_base}: {exc}") from exc

        if not data.get("success"):
            raise RuntimeError(data.get("error") or data)
        return data["data"]


class ServiceRagRunner(RagRunner):
    def __init__(self):
        sys.path.insert(0, str(BACKEND_DIR))
        from config import load_env
        from services.rag_service import get_rag_service

        load_env()
        self.rag_service = get_rag_service()

    def query(self, case: EvalCase, knowledge_base_id: str, top_k: int) -> Dict[str, Any]:
        result = self.rag_service.query(
            question=case.question,
            knowledge_base_id=knowledge_base_id,
            history=case.history or [],
            top_k=case.top_k or top_k,
            temperature=0,
        )
        if not result.get("success"):
            raise RuntimeError(result.get("error") or result)
        return result["data"]


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    score_names = [
        "answer_relevance",
        "answer_accuracy",
        "retrieval_quality",
        "retrieval_recall",
        "retrieval_precision",
        "overall",
    ]
    successful = [result for result in results if "scores" in result]
    failed = [result for result in results if "error" in result]

    averages = {}
    for name in score_names:
        averages[name] = (
            round(sum(result["scores"][name] for result in successful) / len(successful), 4)
            if successful
            else 0.0
        )

    return {
        "total": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "averages": averages,
    }


def write_outputs(output_path: Path, results: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summarize(results),
        "results": results,
    }
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    markdown_path = output_path.with_suffix(".md")
    summary = report["summary"]
    lines = [
        "# RAG Evaluation Report",
        "",
        f"- Total: {summary['total']}",
        f"- Successful: {summary['successful']}",
        f"- Failed: {summary['failed']}",
        f"- Overall: {summary['averages']['overall']:.4f}",
        f"- Answer relevance: {summary['averages']['answer_relevance']:.4f}",
        f"- Answer accuracy: {summary['averages']['answer_accuracy']:.4f}",
        f"- Retrieval quality: {summary['averages']['retrieval_quality']:.4f}",
        "",
        "| Case | Overall | Relevance | Accuracy | Retrieval | Question |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in results:
        if "error" in result:
            lines.append(
                f"| {result['id']} | ERROR | ERROR | ERROR | ERROR | {result.get('question', '')} |"
            )
            continue
        scores = result["scores"]
        question = result["question"].replace("|", "\\|")
        lines.append(
            f"| {result['id']} | {scores['overall']:.4f} | "
            f"{scores['answer_relevance']:.4f} | {scores['answer_accuracy']:.4f} | "
            f"{scores['retrieval_quality']:.4f} | {question} |"
        )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate AnswerMe RAG quality.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=BACKEND_DIR / "evaluation" / "results" / "rag_eval.json")
    parser.add_argument("--knowledge-base-id", default=os.environ.get("EVAL_KNOWLEDGE_BASE_ID"))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--mode",
        choices=["http", "service"],
        default="http",
        help="Use the running FastAPI app or call the service layer directly.",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("EVAL_API_BASE", "http://localhost:8000"),
    )
    parser.add_argument("--fail-under", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = load_dataset(args.dataset)
    runner: RagRunner = (
        HttpRagRunner(args.api_base) if args.mode == "http" else ServiceRagRunner()
    )

    results: List[Dict[str, Any]] = []
    for case in cases:
        knowledge_base_id = case.knowledge_base_id or args.knowledge_base_id
        if not knowledge_base_id:
            results.append(
                {
                    "id": case.id,
                    "question": case.question,
                    "error": "knowledge_base_id is required in dataset or --knowledge-base-id",
                }
            )
            continue

        try:
            rag_result = runner.query(case, knowledge_base_id, args.top_k)
            results.append(evaluate_case(case, rag_result))
        except Exception as exc:
            results.append({"id": case.id, "question": case.question, "error": str(exc)})

    write_outputs(args.output, results)
    summary = summarize(results)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.fail_under is not None and summary["averages"]["overall"] < args.fail_under:
        return 1
    if summary["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
