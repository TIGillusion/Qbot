# 简化版记忆系统 (SimpleMemory)

这个记忆系统是基于MaiBot的海马体记忆机制设计的简化版实现，提供了概念记忆存储、检索、遗忘和整合功能。系统使用图结构存储记忆，并通过激活扩散算法实现基于相关度的记忆检索。

## 功能特点

1. **记忆图结构**：使用图数据结构存储概念和概念间的连接
   - 节点表示概念，存储相关记忆项
   - 边表示概念间的连接，包含连接强度信息

2. **记忆处理**：
   - **记忆构建**：从文本中提取关键概念，为每个概念生成摘要
   - **记忆检索**：通过激活扩散算法查找与输入文本相关的记忆
   - **记忆遗忘**：定期随机遗忘部分记忆，模拟人脑遗忘机制
   - **记忆整合**：合并相似记忆，保留信息量更高的记忆项

3. **相关度计算**：
   - 使用余弦相似度计算文本相似度
   - 基于连接强度的激活扩散模型
   - 多路径激活值累加

## 安装需求

- Python 3.7+
- NetworkX
- jieba
- numpy

安装依赖：

```bash
pip install networkx jieba numpy
```

## 使用方法

### 基本用法

```python
from memory_system import SimpleMemory

# 创建记忆系统实例
memory = SimpleMemory()

# 从文本构建记忆
memory.build_memory_from_text("北京是中国的首都，有着悠久的历史和丰富的文化遗产。")
memory.build_memory_from_text("人工智能技术正在迅速发展，包括机器学习和深度学习。")

# 根据输入文本检索相关记忆
query = "中国的城市"
memories = memory.get_memories_as_string(query)
print(memories)

# 手动执行记忆维护操作
memory.forget_memory()
memory.consolidate_memory()
```

### 运行演示

```bash
cd simple_memory
python demo.py
```

## 参数配置

创建`SimpleMemory`实例时可以自定义以下参数：

```python
memory = SimpleMemory(
    memory_dir="memory_data",            # 记忆数据存储目录
    memory_file="memory_graph.json",     # 记忆图存储文件名
    memory_build_interval=600,           # 记忆构建间隔（秒）
    forget_interval=1000,                # 记忆遗忘间隔（秒）
    consolidate_interval=1000,           # 记忆整合间隔（秒）
    forget_time_hours=24,                # 记忆开始遗忘的时间（小时） 
    forget_percentage=0.01,              # 每次遗忘检查的节点比例
    consolidate_threshold=0.7,           # 记忆整合的相似度阈值
    max_memory_per_node=10               # 每个节点最大记忆项数量
)
```

## 主要方法

- `build_memory_from_text(text)`: 从文本构建记忆
- `get_memories_from_text(text, max_memories)`: 获取与文本相关的记忆列表
- `get_memories_as_string(text, max_memories)`: 获取格式化的记忆字符串
- `forget_memory()`: 执行记忆遗忘
- `consolidate_memory()`: 执行记忆整合
- `save_memory_graph()`: 保存记忆图到文件
- `load_memory_graph()`: 从文件加载记忆图

## 记忆相关度计算原理

系统使用激活扩散算法计算记忆相关度：

1. 从输入文本中提取关键词
2. 为每个关键词节点赋予初始激活值(1.0)
3. 激活扩散到相邻节点，每经过一个连接，激活值减少(1/连接强度)
4. 同一节点可通过多条路径被激活，最终激活值为所有路径激活值之和
5. 按激活值排序选择最相关的记忆

## 记忆遗忘机制

1. 根据节点年龄决定是否可以被遗忘（默认24小时后）
2. 连接数量越多的节点越不易被遗忘
3. 随机决定是否遗忘某个节点的记忆

## 记忆整合机制

1. 检查同一概念下的记忆项相似度
2. 当相似度超过阈值（默认0.7）时，计算各记忆项的信息熵
3. 保留信息量更高的记忆项，删除信息量较低的记忆项

## 限制说明

- 本实现为简化版，不包含LLM调用，主题提取使用jieba分词代替
- 记忆摘要生成使用简单的句子提取，不如LLM生成的摘要精确
- 记忆相关度计算使用词袋模型，不考虑语义理解

## 参考

- 本项目基于MaiBot的海马体记忆系统设计理念
- 激活扩散算法受人脑神经元激活机制启发 