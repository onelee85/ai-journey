# Embedding 笔记

## 1. 什么是 Embedding？

Embedding 是一种将离散数据（如单词、句子、图像等）转换为连续向量空间中的向量表示的技术。它的核心思想是：

- 将高维离散数据映射到低维连续向量空间
- 保持数据之间的语义关系（相似的数据在向量空间中距离更近）
- 使计算机能够更好地理解和处理这些数据

### 基本特点
- **低维性**：相比 one-hot 编码等方法，Embedding 向量维度更低
- **语义保留**：相似含义的实体在向量空间中距离更近
- **泛化能力**：能够捕捉到数据之间的潜在关系
- **可学习性**：通过神经网络等方法自动学习得到

## 2. Embedding 的数学原理

### 向量空间模型
Embedding 基于向量空间模型，将每个实体表示为高维空间中的一个点。

### 相似度计算
- **余弦相似度**：衡量两个向量方向的相似性
  \( \text{cosine similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} \)
- **点积（Dot Product）**：当向量已归一化时，等价于余弦相似度；未归一化时反映向量长度和方向
  \( \text{dot product} = \mathbf{A} \cdot \mathbf{B} = \sum_{i=1}^{n} A_i \cdot B_i \)
- **欧几里得距离**：衡量两个向量在空间中的绝对距离
  \( \text{euclidean distance} = \sqrt{\sum_{i=1}^{n} (A_i - B_i)^2} \)

### 学习方法
- **监督学习**：通过标签数据学习 Embedding
- **无监督学习**：通过数据本身的结构学习 Embedding
- **自监督学习**：利用数据的一部分作为监督信号

### 训练损失函数
- **Contrastive Loss**：拉近正样本对距离，推开负样本对距离
  \( L = -\log \frac{\exp(\text{sim}(a, b)/\tau)}{\sum_{j=1}^{N} \exp(\text{sim}(a, j)/\tau)} \)
- **CoSENT Loss**：基于余弦的排序损失，在中文 Embedding 训练中表现优异
- **Triplet Loss**：最小化锚点与正样本的距离，最大化锚点与负样本的距离

### 降维技术
- **主成分分析 (PCA)**
- **t-SNE**
- **UMAP**

## 3. Embedding 在 NLP 中的应用

### 词嵌入 (Word Embedding)
- **应用场景**：文本分类、情感分析、机器翻译
- **作用**：捕捉词与词之间的语义关系

### 句子嵌入 (Sentence Embedding)
- **应用场景**：文本相似度计算、问答系统、信息检索
- **作用**：将整个句子表示为一个向量

### 文档嵌入 (Document Embedding)
- **应用场景**：文档分类、聚类、推荐系统
- **作用**：捕捉文档的整体语义

### 其他 NLP 任务
- 命名实体识别
- 关系抽取
- 文本生成

### 评估基准
- **MTEB (Massive Text Embedding Benchmark)**：最权威的 Embedding 评估基准，涵盖 58 个数据集、13 种任务类型
  - 支持多语言评估（C-MTEB 为中文子集）
  - 主要评估指标：Borda Count、Mean Average Precision、Mean Reciprocal Rank
- **BEIR**：信息检索领域标准评估基准

## 4. 常见的 Embedding 模型

### 词嵌入模型

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| Word2Vec | 基于预测的词嵌入，有 CBOW 和 Skip-gram 两种架构 | 一般 NLP 任务，计算效率高 |
| GloVe | 基于全局词共现统计的词嵌入 | 需要考虑全局语义的任务 |
| FastText | 考虑词的子词结构 | 处理未登录词，适合形态丰富的语言 |
| ELMo | 基于双向 LSTM 的上下文相关词嵌入 | 需要考虑上下文的任务 |
| BERT | 基于 Transformer 的深度双向语言模型 | 复杂 NLP 任务，需要深度理解 |

### 句子/文档嵌入模型

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| InferSent | 基于双向 LSTM 的句子嵌入 | 句子级任务，如文本相似度 |
| Sentence-BERT | 基于 BERT 的句子嵌入，使用孪生网络结构 | 需要深度语义理解的任务 |
| BGE-M3 | 支持 100+ 语言的稠密向量和稀疏向量混合检索 | 多语言 RAG、跨语言检索 |
| Cohere embed-v4 | 2025 年新模型，1024→768 维度优化，精度提升 30% | 生产级多语言应用 |
| EmbeddingGemma | Google 轻量模型（<500M 参数），支持边缘部署 | 移动端、IoT、设备端 |
| Universal Sentence Encoder | 多任务学习的通用句子编码器 | 迁移学习，跨任务应用 |
| Doc2Vec | 扩展 Word2Vec 到文档级 | 文档分类、聚类 |
| ColBERT | Late Interaction 多向量模型，保留细粒度匹配 | 高精度检索、问答系统 |

## 5. 不同 Embedding 模型的特点和适用场景对比

### 基于频率的方法 vs 基于预测的方法
- **基于频率**：如 GloVe，利用全局统计信息，训练速度快
- **基于预测**：如 Word2Vec，捕捉局部上下文，语义表示更丰富

### 静态 Embedding vs 上下文相关 Embedding
- **静态 Embedding**：如 Word2Vec，每个词有固定的向量表示
- **上下文相关 Embedding**：如 BERT，词的表示依赖于其所在的上下文

### 模型复杂度与性能权衡
- **简单模型**：如 Word2Vec，训练快，资源需求低
- **复杂模型**：如 BERT，性能更好，但训练和推理成本高

### 适用场景推荐
- **资源受限/边缘设备**：EmbeddingGemma、FastText
- **中文场景**：BGE-M3、text2vec（中文 Sentence-BERT）
- **多语言/跨语言**：KaLM-Embedding（腾讯，2025 年 MTEB 多语言第一）、BGE-M3、Cohere embed-v4
- **需要深度理解**：BERT、Sentence-BERT、Cohere embed-v4
- **处理未登录词**：FastText
- **高性能检索**：ColBERT（Late Interaction）
- **灵活维度需求**：Matryoshka Representation（可渐进截断维度）

## 6. 实践应用注意事项

### 预训练 vs 微调
- 预训练 Embedding 可以直接使用，也可以在特定任务上微调
- 微调通常能获得更好的性能

### 领域适配
- 通用 Embedding 在特定领域可能表现不佳
- 可以在领域特定数据上微调或重新训练

### 维度选择与 Matryoshka Representation
- 传统维度选择：100-300 维（精度与效率的平衡）
- **Matryoshka Representation Learning**：允许在同一向量中存储多个粒度的表示，支持灵活截断
  - 如 768 维向量可截断为 512、256、128 维而保持较好性能
  - 适合资源受限的推理场景

### 评估方法
- 内在评估：如词相似度任务
- 外在评估：在具体下游任务上的表现

## 7. 代码示例

### 使用预训练的 Word2Vec
```python
from gensim.models import KeyedVectors

# 加载预训练模型
model = KeyedVectors.load_word2vec_format('path/to/word2vec.bin', binary=True)

# 获取词向量
vector = model['king']

# 计算相似度
similarity = model.similarity('king', 'queen')

# 找最相似的词
similar_words = model.most_similar('king')
```

### 使用 BGE-M3 获取中文句子嵌入
```python
from flag_model import FlagModel

# 加载 BGE-M3 模型（中文场景首选）
model = FlagModel('BAAI/bge-m3', device='cuda')

# 获取句子向量（支持多语言）
sentences = ["这是一个测试句子", "This is a test sentence"]
embeddings = model.encode(sentences)

# 稀疏向量 + 稠密向量混合检索
dense_vec = model.encode("查询内容")  # 稠密向量
sparse_vec = model.encode("查询内容", return_sparse=True)  # 稀疏向量（词项权重）
```

### 使用 Qdrant 进行向量存储和检索
```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# 存储向量
client.upsert(
    collection_name="my_collection",
    points=[{
        "id": 1,
        "vector": [0.1, 0.2, ...],  # 768 维
        "payload": {"text": "要存储的文档", "category": "技术"}
    }]
)

# 检索
results = client.search(
    collection_name="my_collection",
    query_vector=[0.1, 0.2, ...],
    query_filter=None,  # 可添加元数据过滤
    limit=5
)
```
## 向量数据库
### 全面对比：使用场景与优劣
| 维度 | Qdrant | Milvus | Weaviate | pgvector | Chroma | Faiss | Pinecone |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 类型 | 向量数据库 | 分布式向量数据库 | 向量数据库 | PostgreSQL 扩展 | 嵌入式向量数据库 | 向量检索算法库 | 全托管 SaaS |
| 许可 | Apache 2.0 | Apache 2.0 | BSD | PostgreSQL License | Apache 2.0 | Apache 2.0 | 闭源付费 |
| 部署方式 | Docker/K8s/云端 | Docker/K8s 自托管 | Docker/K8s/云端 | PostgreSQL 生态 | pip 嵌入应用 | 代码库嵌入 | 云端 API |
| 易用性 | 高 | 中 | 高 | 高（SQL 生态） | 极高 | 低 | 极高 |
| 分布式能力 | 强（水平扩展） | 极强 | 强 | 中（需 pgvector scale） | 极弱 | 弱 | 自动扩缩容 |
| 数据规模 | 十亿级 | 千亿级 | 十亿级 | 亿级 | 百万级 | 亿级 | 十亿级 |
| 检索性能 | 极高（Rust 实现） | 高 | 高 | 中等（可优化） | 中等 | 极高（GPU） | 高 |
| 运维成本 | 中 | 高 | 中 | 低（SQL 生态） | 极低 | 无 | 无 |
| 混合搜索 | 原生支持（关键词+向量） | 支持 | 原生支持 | 需扩展 | 需扩展 | 需自行实现 | 支持 |
| 过滤能力 | 高级（无性能损失） | 高级 | 高级 | SQL 原生 | 基础 | 有限 | 高级 |
| 典型场景 | RAG、推荐、语义搜索 | 海量数据核心业务 | 多模态 RAG | 中小企业、SQL 集成 | 原型、小工具 | 离线计算、科研 | POC、快速上线 |

#### 2025 年选型趋势
- **pgvector** 正成为中小企业的「默认选择」，零运维成本 + SQL 生态优势
- **Qdrant** 和 **Weaviate** 在开源领域增长最快，尤其适合需要混合搜索的 RAG 场景
- **Chroma** 已不再是轻量首选，Qdrant 的嵌入式模式同样简洁但性能更强

## 学习资源推荐

- [Word2Vec 原始论文](https://papers.nips.cc/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf)
- [GloVe 原始论文](https://nlp.stanford.edu/pubs/glove.pdf)
- [BERT 原始论文](https://arxiv.org/abs/1810.04805)
- [Sentence-BERT 论文](https://arxiv.org/abs/1908.10084)
- [MTEB 基准测试论文](https://arxiv.org/abs/2210.07316)
- [BGE-M3 论文](https://arxiv.org/abs/2401.13514)
- [Cohere embed-v4 发布博客](https://cohere.com/blog/embed-v4)
- [EmbeddingGemma 论文](https://arxiv.org/abs/2509.20354)
- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [Hugging Face Embedding 模型库](https://huggingface.co/models?filter=embeddings)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [OpenAI Embedding API 文档](https://platform.openai.com/docs/guides/embeddings)