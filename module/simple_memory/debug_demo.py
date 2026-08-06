#!/usr/bin/env python
# -*- coding: utf-8 -*-

from memory_system import SimpleMemory
import time
import logging
import os

# 设置日志级别为DEBUG以查看更多详情
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MemoryDebug")

def debug_demo():
    print("===== 记忆系统调试演示 =====")
    
    # 清理旧的测试记忆（如果需要）
    memory_dir = "debug_memory"
    if os.path.exists(os.path.join(memory_dir, "memory_graph.json")):
        os.remove(os.path.join(memory_dir, "memory_graph.json"))
        
    # 创建记忆系统实例，启用调试模式
    memory = SimpleMemory(
        memory_dir=memory_dir, 
        memory_build_interval=0,  # 禁用时间间隔检查
        debug=True  # 启用调试输出
    )
    
    print("\n1. 添加基础记忆测试")
    base_texts = [
        "北京是中国的首都，有着悠久的历史和丰富的文化遗产。长城是中国古代伟大的防御工程，也是世界文化遗产。",
        "上海是中国最大的城市，是重要的经济、金融中心。上海的外滩有许多历史建筑，是著名的旅游景点。"
    ]
    
    for i, text in enumerate(base_texts, 1):
        print(f"\n添加基础记忆 {i}:")
        print(f"'{text[:50]}...'")
        result = memory.maintain_memory(text)
        print(f"构建了 {result['built']} 个新记忆")
    
    # 打印记忆图状态
    node_count = len(memory.memory_graph.nodes())
    edge_count = len(memory.memory_graph.edges())
    print(f"\n当前记忆图状态: {node_count} 个概念, {edge_count} 个连接")
    
    # 查看所有节点
    print("\n当前所有概念:")
    for node in sorted(memory.memory_graph.nodes()):
        memory_items = memory.memory_graph.nodes[node].get("memory_items", [])
        if not isinstance(memory_items, list):
            memory_items = [memory_items]
        print(f"- '{node}': {len(memory_items)} 条记忆")
    
    print("\n2. 记忆查询测试")
    query = "中国的城市"
    print(f"\n查询: '{query}'")
    result = memory.get_memories_as_string(query)
    print(f"结果:\n{result}")
    
    print("\n3. 添加人工智能相关记忆")
    ai_text = "人工智能技术正在迅速发展，包括机器学习、深度学习等多个领域。GPT是一种基于Transformer架构的大型语言模型。"
    result = memory.maintain_memory(ai_text)
    print(f"构建了 {result['built']} 个新记忆")
    
    # 查询AI相关记忆
    query = "什么是人工智能"
    print(f"\n查询: '{query}'")
    result = memory.get_memories_as_string(query)
    print(f"结果:\n{result}")
    
    print("\n4. TF-IDF权重测试")
    # 添加更多带有常见词的记忆
    common_text = "中国有很多城市，每个城市都有其特色。城市化是现代化的重要组成部分。"
    memory.maintain_memory(common_text)
    
    # 添加带有罕见词的记忆
    rare_text = "深圳是中国改革开放的窗口，经济特区的建立推动了中国现代化进程。"
    memory.maintain_memory(rare_text)
    
    # 测试常见词和罕见词查询
    common_query = "中国城市化"  # 包含常见词
    rare_query = "经济特区改革"  # 包含罕见词
    
    print(f"\n常见词查询: '{common_query}'")
    common_result = memory.get_memories_as_string(common_query)
    print(f"结果:\n{common_result}")
    
    print(f"\n罕见词查询: '{rare_query}'")
    rare_result = memory.get_memories_as_string(rare_query)
    print(f"结果:\n{rare_result}")
    
    print("\n5. 复杂查询和长文本测试")
    # 添加长文本记忆
    long_text = """
    智能城市是利用各种信息技术或创新概念，将城市的系统和服务连接起来，以提高资源利用效率，
    优化城市管理和服务，以及改善市民生活质量的城市发展模式。人工智能在智能城市中扮演着重要角色，
    例如智能交通系统可以利用AI分析交通流量，优化信号灯控制，减少拥堵；
    智能电网系统可以预测用电需求，平衡供需关系，提高能源利用效率；
    城市安全监控系统可以利用计算机视觉技术进行异常行为检测和预警。
    """
    
    print("\n添加长文本记忆")
    result = memory.maintain_memory(long_text)
    print(f"构建了 {result['built']} 个新记忆")
    
    # 复杂查询测试
    complex_query = "人工智能在城市中的应用"
    print(f"\n复杂查询: '{complex_query}'")
    complex_result = memory.get_memories_as_string(complex_query)
    print(f"结果:\n{complex_result}")
    
    # 最终记忆图状态
    node_count = len(memory.memory_graph.nodes())
    edge_count = len(memory.memory_graph.edges())
    print(f"\n最终记忆图状态: {node_count} 个概念, {edge_count} 个连接")
    
    # 显示主要概念的连接
    main_concepts = ["中国", "城市", "人工智能", "智能城市"]
    for concept in main_concepts:
        if concept in memory.memory_graph:
            neighbors = list(memory.memory_graph.neighbors(concept))
            print(f"\n概念 '{concept}' 的连接 ({len(neighbors)}):")
            for neighbor in sorted(neighbors)[:5]:
                if concept in memory.memory_graph and neighbor in memory.memory_graph[concept]:
                    strength = memory.memory_graph[concept][neighbor].get("strength", 1)
                    print(f"- '{neighbor}' (强度: {strength})")
    
    print("\n===== 调试演示结束 =====")

if __name__ == "__main__":
    debug_demo() 