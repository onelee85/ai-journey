import os
from dotenv import load_dotenv
import openai
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb

# 以下代码演示了如何使用 RAG 模型进行文档检索、重排和生成。
# 流程如下：
# 1.文档进行切分（语义切分，长度切换）
# 2.切分后的文档片段进行嵌入embedding（文本嵌入模型）
# 3.数据索引- 将嵌入向量存储到向量数据库中
# 用户发起查询请求
# 4.查询请求的文本 进行嵌入embedding
# 5.数据检索 - 将查询请求的嵌入向量与向量数据库中的嵌入向量进行相似度计算
# 6.数据召回 - 根据相似度排序，取Top-K个文档片段
# 7.文档重排 - 对Top-K个文档片段进行重排后的文档片段排序
# 8.文档生成 - 将Top-K个文档片段的文本发给LLM获取回答

# 示例长文档数据
long_document = """
香蕉是草本植物而非木本植物，香蕉树实际上是草本植物中最大的一种，其茎干由叶柄卷曲重叠而成。

蜜蜂可以识别人脸，科学家发现蜜蜂能够记住并识别不同人类的面部特征，准确率可达80%以上。

土豆可以检测水分，其表面含有一种名为"溶血素"的化学物质，当土豆接触水时会发出微弱的电信号。

蜗牛可以睡眠长达三年时间，在干燥或寒冷的环境条件下，某些品种的蜗牛可以进入长达三年的休眠状态。

人类的DNA与香蕉有约60%的相似度，这是因为所有地球生命都来自同一个共同祖先，经过数十亿年进化后的结果。

拿破仑的实际身高约为5英尺7英寸（约170厘米），在当时的法国属于平均身高，所谓"矮子"是英国人的宣传。

考拉的指纹与人类的指纹几乎无法区分，在犯罪现场鉴定中可能造成误判。

宇宙中已知最冷的地方是"回力棒星云"，温度为零下272摄氏度，仅比绝对零度高1度。

番茄酱这个词来源于中国闽南语"ke-tsiap"，经过多次语言演变成为现代英语的ketchup。

金字塔的建造者是被支付的工人而非奴隶，考古发现表明工人墓穴就在金字塔附近，显示出他们受到尊重。

"""


# 文档切分函数
def split_into_chunks(document: str) -> list[str]:
    """将文档文件切分成多个段落"""
    return [chunk for chunk in document.split("\n\n") if chunk.strip()]


chunks = split_into_chunks(long_document)

# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i}: {chunk}\n")


# 嵌入模型
embedding_model = SentenceTransformer("shibing624/text2vec-base-chinese")

# 重排模型 - 全局初始化，避免重复加载
cross_encoder = None


def get_reranker():
    """获取重排模型实例（单例模式）"""
    global cross_encoder
    if cross_encoder is None:
        print("正在加载重排模型...")
        cross_encoder = CrossEncoder(
            "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    return cross_encoder


# 嵌入函数
def embed_chunk(chunk: str) -> list[float]:
    """将段落转换为嵌入向量"""
    return embedding_model.encode(chunk).tolist()


# 对每个段落进行嵌入
embeddings = [embed_chunk(chunk) for chunk in chunks]

# 创建 Chroma 客户端
chromadb_client = chromadb.EphemeralClient()
# 创建或获取集合
collection = chromadb_client.get_or_create_collection("my_collection")


# 保存嵌入向量到 Chroma
def save_embeddings(chunks: list[str], embeddings: list[list[float]]):
    ids = [str(i) for i in range(len(chunks))]
    print(ids)
    """将段落和嵌入向量保存到 Chroma"""
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )


# 保存嵌入向量到 Chroma
save_embeddings(chunks, embeddings)


# 估算文本的 token 数量
def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量（中文约 1.5 tokens/字）"""
    return int(len(text) * 1.5)


# 根据 token 限制选择上下文片段
def select_chunks_by_token_limit(chunks: list[str], max_tokens: int = 2000) -> list[str]:
    """根据 token 限制选择上下文片段"""
    selected = []
    current_tokens = 0
    for chunk in chunks:
        chunk_tokens = estimate_tokens(chunk)
        if current_tokens + chunk_tokens > max_tokens:
            break
        selected.append(chunk)
        current_tokens += chunk_tokens
    return selected


# 召回
def retrieve(query: str, top_k: int = 3) -> list[str]:
    """从 Chroma 中召回最相关的的 top_k 个段落"""
    query_embedding = embed_chunk(query)
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results["documents"][0]

# 重排


def rerank(query: str, retrieved_chunks: list[str], top_k: int = 3) -> list[str]:
    """使用 OpenAI 的 Ranker 模型对段落进行重排"""
    reranker = get_reranker()
    pairs = [(query, chunk) for chunk in retrieved_chunks]
    scores = reranker.predict(pairs)
    ranked_chunks = sorted(zip(retrieved_chunks, scores),
                           key=lambda x: x[1], reverse=True)[:top_k]
    return [chunk for chunk, _ in ranked_chunks]


# 可视化评估结果
def print_evaluation(evaluation: dict):
    """格式化输出评估结果"""
    print("\n评估结果：")
    print(f"  ├─ 回答长度: {evaluation['answer_length']} 字")
    print(f"  ├─ 上下文覆盖: {evaluation['context_coverage']} 个片段")
    print(f"  ├─ 引用片段: {'是' if evaluation['has_citation'] else '否'}")
    print(f"  ├─ 信息充足: {'否' if evaluation['has_uncertainty'] else '是'}")
    print(f"  ├─ 置信度: {evaluation['confidence'].upper()}")
    print(f"  └─ 长度评分: {evaluation['length_score']}")


# 调用 OpenAI 模型
# 加载环境变量
load_dotenv()
# 配置 LM Studio 本地 API 端点
api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
# LM Studio 使用 "lm-studio" 作为 API key
api_key = os.getenv("LM_STUDIO_API_KEY")

# 创建OpenAI客户端
client_openai = openai.OpenAI(
    base_url=api_base,
    api_key=api_key
)


# 生成回答
# 提示词模板 - 包含角色定义、输出格式和思考步骤
def create_prompt(query: str, chunks: list[str]) -> str:
    """创建结构化的提示词模板"""
    chunks_text = "\n\n".join(
        [f"片段 {i+1}:\n{chunk}" for i, chunk in enumerate(chunks)])

    prompt = f"""
    # 角色定义
    你是一个专业的信息助手，擅长基于给定的上下文回答问题。
    
    # 任务要求
    - 请基于以下提供的相关片段回答用户问题
    - 如果上下文不足以回答问题，请明确说明"信息不足"
    - 禁止编造信息或使用外部知识
    - 回答需要条理清晰，引用相关片段
    
    # 输出格式
    1. 直接回答问题
    2. 引用相关片段来源（如：根据片段 1）
    3. 如果信息不足，明确说明
    
    # 思考步骤
    1. 分析用户问题的核心需求
    2. 从提供的片段中提取相关信息
    3. 整合信息形成回答
    4. 检查回答是否基于给定上下文
    
    # 用户问题
    {query}
    
    # 相关片段
    {chunks_text}
    
    # 请开始回答：
    """
    return prompt


def generate(query: str, chunks: list[str]) -> tuple[str, dict]:
    """使用大模型模型生成回答，并返回评估信息"""
    chunks_text = "\n".join(chunks)
    prompt = create_prompt(query, chunks)

    response = client_openai.chat.completions.create(
        model="qwen3.5-2b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    answer = response.choices[0].message.content

    # 返回回答和评估信息
    evaluation = evaluate_answer(query, answer, chunks)
    return answer, evaluation


def evaluate_answer(query: str, answer: str, chunks: list[str]) -> dict:
    """评估回答质量"""
    # 计算回答长度（字符数）
    answer_length = len(answer)

    # 计算使用的上下文数量
    context_coverage = len(chunks)

    # 检查是否引用了片段（简单的关键词匹配）
    has_citation = any(
        f"片段 {i+1}" in answer or f"片段{i+1}" in answer
        for i in range(len(chunks))
    )

    # 检查回答是否包含"信息不足"的提示
    has_uncertainty = any(
        phrase in answer
        for phrase in ["信息不足", "无法确定", "没有提到", "不清楚"]
    )

    # 评估置信度
    if has_uncertainty or context_coverage == 0:
        confidence = "low"
    elif has_citation and answer_length > 20:
        confidence = "high"
    else:
        confidence = "medium"

    # 评估回答长度是否合理
    if answer_length < 10:
        length_score = "too_short"
    elif answer_length < 50:
        length_score = "short"
    elif answer_length < 200:
        length_score = "adequate"
    else:
        length_score = "detailed"

    return {
        "answer_length": answer_length,
        "context_coverage": context_coverage,
        "has_citation": has_citation,
        "has_uncertainty": has_uncertainty,
        "confidence": confidence,
        "length_score": length_score
    }


if __name__ == "__main__":
    print("RAG 模型演示")
    print("="*50)

    # 测试查询
    query = "蜗牛会休眠吗？"
    print(f"\n查询：{query}\n")

    # 召回不同数量的片段进行测试
    for top_k in [3, 5]:
        print(f"\n--- 测试 top_k={top_k} ---")
        retrieved = retrieve(query, top_k=top_k)

        # 测试不同的上下文窗口管理策略
        print(f"\n召回的片段数量：{len(retrieved)}")
        for i, chunk in enumerate(retrieved):
            tokens = estimate_tokens(chunk)
            print(f"  片段 {i+1}: {len(chunk)} 字, 估算 {tokens} tokens")

        # 使用 token 限制选择上下文
        limited_chunks = select_chunks_by_token_limit(
            retrieved, max_tokens=2000)
        print(f"\n应用 token 限制后：{len(limited_chunks)} 个片段")

        # 调用重排
        reranked = rerank(query, limited_chunks)
        print(f"重排后的片段数量：{len(reranked)}")

        # 生成回答并评估
        answer, evaluation = generate(query, reranked)
        print(f"\n回答：{answer}")
        print_evaluation(evaluation)

        print("\n" + "-"*50)

    # 测试不同 top_k 的效果对比
    print("\n\n=== 效果对比 ===")

    # 测试不同的 top_k 值
    test_queries = [
        "蜗牛会休眠吗？",  # 简单查询
        "人类和香蕉有什么关系？",  # 复杂查询
        "金字塔是谁建造的？",  # 简单查询
    ]

    for query in test_queries:
        print(f"\n\n查询：{query}")
        print("-" * 60)

        results = []
        for top_k in [3, 5, 10]:
            retrieved = retrieve(query, top_k=top_k)
            limited = select_chunks_by_token_limit(retrieved, max_tokens=2000)
            reranked = rerank(query, limited)
            answer, eval_info = generate(query, reranked)

            results.append({
                "top_k": top_k,
                "context": len(limited),
                "confidence": eval_info['confidence'],
                "length": eval_info['answer_length']
            })

            print(f"top_k={top_k:2d} | 上下文: {len(limited)} 片段 | "
                  f"置信度: {eval_info['confidence']:6s} | "
                  f"长度: {eval_info['answer_length']:3d} 字 | "
                  f"引用: {'是' if eval_info['has_citation'] else '否'}")

        # 分析结果
        best = max(results, key=lambda x: x['confidence'] == 'high')
        print(f"\n最佳配置: top_k={best['top_k']} (置信度: {best['confidence']})")
