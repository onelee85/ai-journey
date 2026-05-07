# RAG Evaluation

This folder contains a lightweight automated evaluation workflow for AnswerMe.

It covers three steps:

1. Create a dataset with questions, expected answers, and expected sources.
2. Run the RAG application on those questions.
3. Score answer relevance, answer accuracy, and retrieval quality.

## Dataset Format

Use JSONL. Each line is one evaluation case:

```json
{"id":"ml_definition","question":"什么是机器学习？","expected_answer":"机器学习是让计算机从数据中学习规律，并使用这些规律进行预测或决策的方法。","expected_sources":["机器学习入门.md"],"must_include":["数据","学习","预测"],"must_not_include":["等同于深度学习"]}
```

Supported fields:

- `id`: Stable case id.
- `question`: User question.
- `knowledge_base_id`: Optional. If omitted, pass `--knowledge-base-id`.
- `expected_answer`: Reference answer used for answer accuracy.
- `expected_sources`: Expected source filenames or file paths.
- `expected_source_ids`: Expected document ids.
- `must_include`: Phrases that must appear in the answer.
- `must_not_include`: Phrases that must not appear in the answer.
- `history`: Optional chat history.
- `top_k`: Optional per-case retrieval top K.

## Run Against The FastAPI App

Start the backend first:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Then run:

```bash
cd backend
source venv/bin/activate
python evaluation/evaluate_rag.py \
  --dataset evaluation/sample_dataset.jsonl \
  --knowledge-base-id <kb_id> \
  --mode http
```

## Run Directly Against The Service Layer

```bash
cd backend
source venv/bin/activate
python evaluation/evaluate_rag.py \
  --dataset evaluation/sample_dataset.jsonl \
  --knowledge-base-id <kb_id> \
  --mode service
```

## Outputs

By default the script writes:

- `backend/evaluation/results/rag_eval.json`
- `backend/evaluation/results/rag_eval.md`

The summary includes:

- `answer_relevance`: lexical overlap between question and answer.
- `answer_accuracy`: overlap with expected answer plus `must_include` and `must_not_include` checks.
- `retrieval_quality`: expected source recall and precision in returned `sources`.
- `overall`: weighted score for CI or regression tracking.

Use a threshold in automation:

```bash
python evaluation/evaluate_rag.py \
  --dataset evaluation/sample_dataset.jsonl \
  --knowledge-base-id <kb_id> \
  --fail-under 0.70
```
