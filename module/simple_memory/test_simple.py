from memory_system import SimpleMemory
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def simple_test():
    print("===== 简单测试脚本 =====")
    
    # 创建记忆系统实例
    memory = SimpleMemory(memory_dir="test_memory")
    
    # 添加记忆
    text = "北京是中国的首都，有着悠久的历史和丰富的文化遗产。"
    print(f"添加文本: '{text}'")
    
    result = memory.maintain_memory(text)
    print(f"构建了 {result['built']} 个记忆")
    
    # 查询记忆
    query = "中国的城市"
    print(f"\n查询: '{query}'")
    
    result = memory.get_memories_as_string(query)
    print(f"结果: {result}")
    
    # 打印记忆图状态
    print(f"\n记忆图状态: {len(memory.memory_graph.nodes())} 个概念, {len(memory.memory_graph.edges())} 个连接")
    
    print("\n===== 测试结束 =====")

if __name__ == "__main__":
    simple_test() 