import os
import time
from dotenv import load_dotenv
import openai
import chromadb

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

# 示例文档数据
documents = [
    "人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。",
    "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进性能，而不需要明确的编程。",
    "深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的学习过程。",
    "自然语言处理是人工智能的一个领域，它使计算机能够理解、解释和生成人类语言。",
    "计算机视觉是人工智能的一个领域，它使计算机能够理解和解释图像和视频。",
    "强化学习是机器学习的一种方法，它通过试错和奖励机制来学习最优行为。",
    "数据挖掘是从大量数据中发现模式和知识的过程。",
    "神经网络是一种模仿人脑结构和功能的计算模型，用于机器学习和人工智能。",
    "监督学习是机器学习的一种方法，它使用标记的数据来训练模型。",
    "无监督学习是机器学习的一种方法，它使用未标记的数据来发现模式。"
]

# 创建Chroma客户端
client_chroma = chromadb.Client()

# 创建或获取集合
collection = client_chroma.create_collection(
    name="ai_documents", get_or_create=True)

# 为文档生成嵌入并添加到集合
print("创建向量数据库...")
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
    metadatas=[{"source": f"doc_{i}"} for i in range(len(documents))]
)

end_time = time.time()
print(f"向量数据库创建完成，耗时: {end_time - start_time:.4f}秒")

# 测试向量搜索
print("\n测试向量搜索:")
query = "什么是机器学习？"

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

print(f"搜索完成，耗时: {end_time - start_time:.4f}秒")
print(f"查询: {query}")
print("搜索结果:")
for i, (doc, distance) in enumerate(zip(results["documents"][0], results["distances"][0])):
    print(f"{i+1}. {doc} (相似度: {1 - distance:.4f})")

print("\n向量搜索演示完成！")
