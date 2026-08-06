from memory_system import SimpleMemory
import os

def write_to_file(text):
    with open("test_output.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def file_output_test():
    # 清空输出文件
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write("===== 测试开始 =====\n")
    
    write_to_file("创建记忆系统...")
    
    # 创建记忆系统实例
    memory = SimpleMemory(memory_dir="file_test_memory")
    
    # 添加记忆
    text = "北京是中国的首都，有着悠久的历史和丰富的文化遗产。"
    write_to_file(f"添加文本: '{text}'")
    
    result = memory.maintain_memory(text)
    write_to_file(f"构建了 {result['built']} 个新记忆")
    
    # 查询记忆
    query = "中国的城市"
    write_to_file(f"\n查询: '{query}'")
    
    result = memory.get_memories_as_string(query)
    write_to_file(f"结果: {result}")
    
    # 打印记忆图状态
    write_to_file(f"\n记忆图状态: {len(memory.memory_graph.nodes())} 个概念, {len(memory.memory_graph.edges())} 个连接")
    
    write_to_file("\n===== 测试结束 =====")

if __name__ == "__main__":
    file_output_test()
    print("测试完成，请查看test_output.txt文件") 