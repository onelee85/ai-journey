import os
import time
from dotenv import load_dotenv
import openai
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

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

# 示例长文档数据
long_document = """人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。

机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进性能，而不需要明确的编程。机器学习算法可以从数据中识别模式，并使用这些模式来做出预测或决策。

深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的学习过程。深度学习在图像识别、语音识别、自然语言处理等领域取得了显著的成果。

自然语言处理是人工智能的一个领域，它使计算机能够理解、解释和生成人类语言。自然语言处理技术包括文本分类、情感分析、机器翻译等。

计算机视觉是人工智能的一个领域，它使计算机能够理解和解释图像和视频。计算机视觉技术包括对象检测、图像分割、人脸识别等。

强化学习是机器学习的一种方法，它通过试错和奖励机制来学习最优行为。强化学习在游戏、机器人控制等领域有广泛应用。

数据挖掘是从大量数据中发现模式和知识的过程。数据挖掘技术包括关联规则学习、聚类分析、异常检测等。

神经网络是一种模仿人脑结构和功能的计算模型，用于机器学习和人工智能。神经网络由神经元和连接组成，可以通过训练学习复杂的模式。

监督学习是机器学习的一种方法，它使用标记的数据来训练模型。监督学习算法包括线性回归、逻辑回归、支持向量机等。

无监督学习是机器学习的一种方法，它使用未标记的数据来发现模式。无监督学习算法包括聚类、降维、关联规则学习等。"""


# 文档切分函数
def split_by_length(document, chunk_size=200, chunk_overlap=20):
    """基于长度的文档切分"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(document)


def split_by_semantic(document, chunk_size=100):
    """基于语义的文档切分"""
    splitter = SentenceTransformersTokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0
    )
    return splitter.split_text(document)


# 执行文档切分
print("\n=== 文档切分演示 ===")
print("原始文档长度:", len(long_document))

# 基于长度的切分
length_chunks = split_by_length(long_document)
print(f"\n基于长度切分结果: {len(length_chunks)} 个片段")
for i, chunk in enumerate(length_chunks[:3]):
    print(f"片段 {i+1}: {chunk[:100]}...")

# 基于语义的切分
semantic_chunks = split_by_semantic(long_document)
print(f"\n基于语义切分结果: {len(semantic_chunks)} 个片段")
for i, chunk in enumerate(semantic_chunks[:3]):
    print(f"片段 {i+1}: {chunk[:100]}...")

# 使用切分后的文档
documents = length_chunks

# 创建Chroma客户端
client_chroma = chromadb.Client()

# 创建或获取集合
collection = client_chroma.create_collection(
    name="ai_documents", get_or_create=True)

# 清空集合（可选）
# collection.delete(ids=[f"doc_{i}" for i in range(len(documents))])

# 为文档生成嵌入并添加到集合
print("\n创建向量数据库...")
start_time = time.time()

# 生成嵌入
response = client_openai.embeddings.create(
    model="text-embedding-qwen3-embedding-0.6b",
    input=documents
)

embeddings = [item.embedding for item in response.data]

# 添加到集合
collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))],
    metadatas=[{"source": f"doc_{i}", "chunk_type": "length_split"}
               for i in range(len(documents))]
)

end_time = time.time()
print(f"向量数据库创建完成，耗时: {end_time - start_time:.4f}秒")
print(f"添加了 {len(documents)} 个文档片段")

# 测试向量搜索
print("\n测试向量搜索:")
queries = ["什么是机器学习？", "深度学习的应用", "自然语言处理技术"]

for query in queries:
    # 为查询生成嵌入
    query_embedding = client_openai.embeddings.create(
        model="text-embedding-qwen3-embedding-0.6b",
        input=[query]
    ).data[0].embedding

    start_time = time.time()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    end_time = time.time()

    print(f"\n查询: {query}")
    print(f"搜索完成，耗时: {end_time - start_time:.4f}秒")
    print("搜索结果:")
    for i, (doc, distance) in enumerate(zip(results["documents"][0], results["distances"][0])):
        print(f"{i+1}. {doc} (相似度: {1 - distance:.4f})")

# 测试不同切分策略的效果
print("\n=== 不同切分策略对比 ===")
print(f"基于长度切分: {len(length_chunks)} 个片段")
print(f"基于语义切分: {len(semantic_chunks)} 个片段")

print("\n向量搜索演示完成！")
