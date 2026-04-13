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
    crossEncoder = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    pairs = [(query, chunk) for chunk in retrieved_chunks]
    scores = crossEncoder.predict(pairs)
    ranked_chunks = sorted(zip(retrieved_chunks, scores),
                           key=lambda x: x[1], reverse=True)[:top_k]
    return [chunk for chunk, _ in ranked_chunks]


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
def generate(query: str, chunks: list[str]) -> str:
    chunks_text = "\n".join(chunks)
    prompt = f"""
    用户问题：{query}
    相关片段：{chunks_text}
    请基于上述内容作答，不要编造信息
    """

    """使用大模型模型生成回答"""
    response = client_openai.chat.completions.create(
        model="qwen3.5-2b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("RAG 模型演示")
    print("="*50)
    query = "蜗牛会休眠吗？"
    retrieved = retrieve(query, top_k=5)
    # 调用重排
    reranked = rerank(query, retrieved)
    answer = generate(query, reranked)
    print(query)
    answer = generate(query, reranked)
    print(answer)
