import tiktoken

# 定义模型名称
model_name = "gpt-4o"

# 加载模型编码器
encoding = tiktoken.encoding_for_model(model_name)

text = "Hello world, 你好世界"

tokens = encoding.encode(text)

print(tokens)
print(f"文本 {text} 的 token 数量: {len(tokens)}")
