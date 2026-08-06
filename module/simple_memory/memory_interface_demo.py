#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_memory.memory_interface import add_memory, query_memory
import os

def main():
    # 设置记忆路径
    memory_path = "demo_memory"
    
    # 确保记忆目录存在
    os.makedirs(memory_path, exist_ok=True)
    
    # 示例1：添加单条记忆
    print("===== 添加记忆示例 =====")
    memory_text = "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    result = add_memory(memory_text, memory_path)
    print(f"添加结果: {result}")
    
    # 示例2：添加更多记忆
    memories = [
        "深度学习是机器学习的一个分支，使用多层神经网络进行数据处理和特征学习。",
        "自然语言处理是人工智能的一个子领域，专注于计算机理解、解释和生成人类语言。",
        "计算机视觉是人工智能领域的一部分，致力于让计算机理解和处理视觉信息。"
    ]
    
    for memory in memories:
        add_memory(memory, memory_path)
    
    # 示例3：查询记忆
    print("\n===== 查询记忆示例 =====")
    queries = [
        "什么是人工智能",
        "深度学习",
        "计算机如何处理语言"
    ]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        result = query_memory(query, memory_path)
        print(f"结果:\n{result}")

if __name__ == "__main__":
    main() 