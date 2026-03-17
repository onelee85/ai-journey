# Function Calling 核心概念笔记

## 一、函数描述（Function Schema）

### 1.1 概述

函数描述是告诉LLM"可以调用什么函数"的元数据定义，是Function Calling的核心组件。

### 1.2 函数描述结构

```json
{
  "name": "函数名称",
  "description": "函数功能描述",
  "parameters": {
    "type": "object",
    "properties": {
      "参数名": {
        "type": "数据类型",
        "description": "参数说明"
      }
    },
    "required": ["必需参数列表"]
  }
}
```

### 1.3 函数描述要素

#### **name（函数名称）**

- 唯一标识符，由字母、数字、下划线组成
- 应具有描述性，清晰表达函数功能
- 示例：`get_weather`, `calculate`, `search`

#### **description（函数描述）**

- 详细说明函数的功能和用途
- 帮助模型理解何时以及如何调用该函数
- 应包含：功能描述、使用场景、预期输入

#### **parameters（参数定义）**

- **type**: 通常为 "object"
- **properties**: 参数详细定义
  - **type**: 数据类型（string, integer, number, boolean, array, object）
  - **description**: 参数说明
  - **enum**: 可选值枚举
  - **items**: 数组元素定义
- **required**: 必需参数列表（字符串数组）

## 二、模型调用流程

### 2.1 概述

函数调用是指可靠地连接LLM与外部工具的能力。让用户能够使用高效的外部工具、与外部API进行交互。

### 2.2 详细步骤

#### **步骤1: 用户输入**

- 用户提出问题或请求
- 示例："今天北京天气怎么样？"

#### **步骤2: 模型分析意图**

- 模型分析用户输入
- 判断是否需要调用函数
- 识别需要调用的函数和参数

#### **步骤3: 函数调用请求**

graph TD
A[用户提问] --> B[开发者：发送「问题+预定义函数清单」给LLM]
B --> C[LLM分析需求：判断是否需要调用函数]
C -->|不需要| Z[LLM直接返回自然语言回答]
C -->|需要| D[LLM返回：函数名 + 调用参数（JSON格式）]
D --> E[开发者：本地/服务端执行对应函数，获取真实结果]
E --> F[开发者：发送「函数结果」给LLM]
F --> G[LLM整合结果，返回自然语言回答]

模型返回特定格式的响应：

```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\": \"北京\", \"date\": \"2024-03-17\"}"
      }
    }
  ]
}
```

#### **步骤4: 执行函数**

- 应用程序解析函数调用请求
- 执行实际的函数逻辑
- 获取函数执行结果

#### **步骤5: 返回函数结果**

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "{\"city\": \"北京\", \"temperature\": \"15°C\", \"condition\": \"晴天\"}"
}
```

#### **步骤6: 生成最终回答**

- 模型接收函数结果
- 生成自然语言回答
- 返回给用户

### 2.3 单轮 vs 多轮调用

#### **单轮调用**

- 一次用户输入 → 一次函数调用 → 一次回答
- 适用于简单场景

#### **多轮调用**

- 一次用户输入 → 多次函数调用 → 一次回答
- 适用于复杂场景，需要多个函数协同

### 2.4 无函数调用场景

- 如果用户问题不需要调用函数
- 模型直接生成自然语言回答
- 流程：用户输入 → 模型分析 → 直接回答

***

## 三、参数定义与验证

### 3.1 参数类型

#### **基本类型**

- `string`: 字符串
- `integer`: 整数
- `number`: 数字（整数或浮点数）
- `boolean`: 布尔值
- `array`: 数组
- `object`: 对象

#### **高级定义**

**枚举类型（enum）**

```json
{
  "type": "string",
  "enum": ["晴天", "雨天", "阴天", "雪天"],
  "description": "天气状况"
}
```

**数组类型**

```json
{
  "type": "array",
  "items": {
    "type": "string"
  },
  "description": "标签列表"
}
```

**嵌套对象**

```json
{
  "type": "object",
  "properties": {
    "lat": {"type": "number"},
    "lon": {"type": "number"}
  },
  "required": ["lat", "lon"]
}
```

### 3.2 参数验证

#### **服务器端验证**

- 类型验证
- 必填参数检查
- 范围验证（最小值、最大值）
- 格式验证（邮箱、URL等）

#### **客户端验证**

- 在调用函数前验证参数
- 提供友好的错误提示
- 防止无效请求

### 3.3 默认值设置

```json
{
  "type": "integer",
  "description": "返回结果数量",
  "default": 10,
  "minimum": 1,
  "maximum": 100
}
```

### 3.4 参数示例

#### 复杂参数定义

```json
{
  "name": "flight_search",
  "description": "搜索航班信息",
  "parameters": {
    "type": "object",
    "properties": {
      "origin": {
        "type": "string",
        "description": "出发城市或机场"
      },
      "destination": {
        "type": "string",
        "description": "到达城市或机场"
      },
      "date": {
        "type": "string",
        "format": "date",
        "description": "出发日期，格式：YYYY-MM-DD"
      },
      "passengers": {
        "type": "integer",
        "description": "乘客数量",
        "default": 1,
        "minimum": 1,
        "maximum": 9
      },
      "class": {
        "type": "string",
        "enum": ["经济舱", "商务舱", "头等舱"],
        "description": "舱位等级",
        "default": "经济舱"
      },
      "nonstop": {
        "type": "boolean",
        "description": "是否只搜索直飞航班",
        "default": false
      }
    },
    "required": ["origin", "destination", "date"]
  }
}
```

### 3.5 错误处理

#### **参数缺失**

```python
if missing_params:
    return {"error": f"缺少必需参数: {', '.join(missing_params)}"}
```

#### **类型错误**

```python
if not isinstance(value, expected_type):
    return {"error": f"参数 {key} 类型错误，期望: {expected_type}"}
```

#### **范围错误**

```python
if value < min_value or value > max_value:
    return {"error": f"参数 {key} 超出范围 [{min_value}, {max_value}]"}
```

***

## 四、最佳实践

### 4.1 函数设计原则

1. **单一职责**：每个函数只做一件事
2. **清晰命名**：函数名应明确表达功能
3. **详细描述**：函数描述应包含使用场景
4. **最小参数**：只包含必需的参数

### 4.2 参数设计原则

1. **类型明确**：使用正确的数据类型
2. **描述清晰**：每个参数都有清晰的说明
3. **合理默认**：为常用值设置默认值
4. **范围限制**：为数值参数设置合理范围

### 4.3 调用流程优化

1. **错误处理**：完善的错误处理机制
2. **重试策略**：网络请求的重试机制
3. **缓存优化**：缓存常用查询结果
4. **日志记录**：记录调用过程便于调试

### 4.4 安全考虑

1. **参数验证**：严格验证所有输入参数
2. **权限控制**：限制敏感函数的调用
3. **速率限制**：防止滥用API
4. **日志脱敏**：敏感信息脱敏处理

***

## 五、常见问题

### Q1: 何时使用Function Calling？

- 需要获取实时数据（天气、股票等）
- 需要执行计算或逻辑操作
- 需要查询数据库或API
- 需要执行特定业务逻辑

### Q2: Function Calling vs 直接Prompt？

- Function Calling：适合结构化输出和外部API调用
- 直接Prompt：适合自由格式的回答和知识问答

### Q3: 如何提高函数调用准确率？

- 清晰的函数描述
- 准确的参数定义
- 提供调用示例
- 使用合适的模型（如gpt-4o-mini）

***

</file>
