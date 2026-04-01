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
  \[ \text{cosine similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} \]
- **欧几里得距离**：衡量两个向量在空间中的距离
  \[ \text{euclidean distance} = \sqrt{\sum_{i=1}^{n} (A_i - B_i)^2} \]

### 学习方法
- **监督学习**：通过标签数据学习 Embedding
- **无监督学习**：通过数据本身的结构学习 Embedding
- **自监督学习**：利用数据的一部分作为监督信号

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
| Sentence-BERT | 基于 BERT 的句子嵌入 | 需要深度语义理解的任务 |
| Universal Sentence Encoder | 多任务学习的通用句子编码器 | 迁移学习，跨任务应用 |
| Doc2Vec | 扩展 Word2Vec 到文档级 | 文档分类、聚类 |

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
- **资源受限场景**：Word2Vec、GloVe
- **需要深度理解**：BERT、Sentence-BERT
- **处理未登录词**：FastText
- **跨语言任务**：多语言 BERT、Universal Sentence Encoder

## 6. 实践应用注意事项

### 预训练 vs 微调
- 预训练 Embedding 可以直接使用，也可以在特定任务上微调
- 微调通常能获得更好的性能

### 领域适配
- 通用 Embedding 在特定领域可能表现不佳
- 可以在领域特定数据上微调或重新训练

### 向量维度选择
- 维度越高，表达能力越强，但计算成本也越高
- 通常选择 100-300 维的向量

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

### 使用 BERT 获取句子嵌入
```python
from sentence_transformers import SentenceTransformer

# 加载预训练模型
model = SentenceTransformer('all-MiniLM-L6-v2')

# 获取句子向量
sentences = ["This is a sentence", "This is another sentence"]
embeddings = model.encode(sentences)

# 计算相似度
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
```

## 8. 学习资源推荐

- [Word2Vec 原始论文](https://papers.nips.cc/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf)
- [GloVe 原始论文](https://nlp.stanford.edu/pubs/glove.pdf)
- [BERT 原始论文](https://arxiv.org/abs/1810.04805)
- [Sentence-BERT 论文](https://arxiv.org/abs/1908.10084)
- [Hugging Face Embedding 模型库](https://huggingface.co/models?filter=embeddings)
- [OpenAI Embedding API 文档](https://platform.openai.com/docs/guides/embeddings)