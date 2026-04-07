import openai
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


# 配置 LM Studio 本地 API 端点
openai.api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
# LM Studio 使用 "lm-studio" 作为 API key
openai.api_key = os.getenv("LM_STUDIO_API_KEY")

# 创建客户端
client = openai.OpenAI(
    base_url=openai.api_base,
    api_key=openai.api_key
)


def test_embedding():

    # 定义文本
    texts = [
        "猫是一种宠物",
        "狗是一种宠物",
        "苹果是一种水果",
        "香蕉是一种水果",
    ]

    # 调用 embedding API
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-qwen3-embedding-0.6b"
    )

    # 提取嵌入向量
    embeddings = [item.embedding for item in response.data]

    # 打印结果
    print(f"生成的嵌入向量数量: {len(embeddings)}")
    print(f"每个向量的维度: {len(embeddings[0])}")

    # 计算相似度矩阵
    similarity_matrix = cosine_similarity(embeddings)

    # 打印相似度
    print("文本相似度矩阵:")
    for i, text1 in enumerate(texts):
        for j, text2 in enumerate(texts):
            if i < j:  # 只打印上三角矩阵，避免重复
                print(
                    f"'{text1[:20]}...' 与 '{text2[:20]}...' 的相似度: {similarity_matrix[i][j]:.4f}")


if __name__ == "__main__":
    test_embedding()
