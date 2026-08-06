#!/usr/bin/env python
# -*- coding: utf-8 -*-

from memory_system import SimpleMemory
import time
import logging
import os

# 设置日志级别为DEBUG以查看更多详情
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MemoryDemo")

def demo():
    # 创建记忆系统实例
    memory = SimpleMemory(memory_dir="demo_memory")
    
    print("===== 简化版记忆系统演示 =====")
    print("初始化记忆系统...")
    
    # 添加一些初始记忆
    print("\n1. 添加初始记忆")
    texts = [
        "北京是中国的首都，有着悠久的历史和丰富的文化遗产。长城是中国古代伟大的防御工程，也是世界文化遗产。",
        "上海是中国最大的城市，是重要的经济、金融中心。上海的外滩有许多历史建筑，是著名的旅游景点。",
        "人工智能技术正在迅速发展，包括机器学习、深度学习等多个领域。GPT是一种基于Transformer架构的大型语言模型。",
        "太空探索是人类探索宇宙奥秘的伟大冒险。火星是太阳系内最接近地球的行星之一，被认为是未来人类移民的潜在目标。",
        "气候变化是当今世界面临的最严峻挑战之一，全球变暖导致极端天气事件增多。减少碳排放是应对气候变化的重要措施。",
        "健康饮食包括多种蔬菜水果、全谷物和优质蛋白质，减少加工食品和糖的摄入。规律运动能够增强体质，预防疾病。",
        "区块链技术是一种分布式账本技术，通过密码学保证交易的安全性和不可篡改性。比特币是第一个基于区块链的加密货币。",
        "量子计算利用量子力学原理，如叠加和纠缠，进行计算。量子计算机有潜力解决传统计算机难以处理的复杂问题。",
        "自然语言处理是人工智能的一个分支，专注于让计算机理解和处理人类语言。情感分析、机器翻译和问答系统是NLP的重要应用。"
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"\n添加文本 {i}:")
        print(f"'{text[:50]}...'")
        result = memory.maintain_memory(text)
        print(f"构建了 {result['built']} 个新记忆")
    
    # 查询记忆，但不将查询添加到记忆中
    print("\n2. 基本记忆查询测试")
    
    queries = [
        "中国的城市有哪些？",
        "什么是人工智能？",
        "北京有什么著名景点？",
        "太空探索的目标是什么？",
        "如何应对气候变化？"
    ]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        result = memory.get_memories_as_string(query)
        print(result)
    
    # 执行记忆维护任务
    print("\n3. 执行记忆维护")
    print("等待几秒钟...")
    time.sleep(3)  # 等待一段时间，模拟时间流逝
    
    # 执行记忆维护，但不添加新记忆
    result = memory.maintain_memory()
    print(f"遗忘了 {result['forgotten']} 个记忆")
    print(f"整合了 {result['consolidated']} 个记忆")
    
    # 添加新记忆并检索
    print("\n4. 添加新记忆并查询")
    new_texts = [
        "深圳是中国改革开放的窗口，是一座现代化的国际化城市。深圳毗邻香港，是中国重要的科技创新中心。",
        "杭州是浙江省省会，以西湖风景名胜而闻名，也是电子商务巨头阿里巴巴的总部所在地。",
        "成都是四川省省会，以美食和熊猫而闻名于世，是中国西南地区重要的经济中心。"
    ]
    
    # 先执行维护，添加新记忆
    for text in new_texts:
        print(f"\n添加新记忆: '{text[:50]}...'")
        memory.maintain_memory(text)
    
    # 然后进行查询
    print("\n新记忆添加后查询:")
    queries = [
        "中国的现代化城市",
        "中国的科技创新中心",
        "中国有哪些著名景点"
    ]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        result = memory.get_memories_as_string(query)
        print(result)
    
    # TF-IDF 效果演示
    print("\n5. TF-IDF权重效果演示")
    common_words_query = "中国的城市是什么样的"  # 包含常见词"中国"、"城市"、"是"等
    rare_words_query = "深圳特区建设和改革开放"  # 包含较少见的词"特区"、"改革开放"等
    
    print(f"\n常见词查询: '{common_words_query}'")
    result1 = memory.get_memories_as_string(common_words_query)
    print(result1)
    
    print(f"\n罕见词查询: '{rare_words_query}'")
    result2 = memory.get_memories_as_string(rare_words_query)
    print(result2)
    
    # 复杂混合主题查询
    print("\n6. 复杂混合主题查询")
    complex_queries = [
        "人工智能在城市建设中的应用",  # 混合AI和城市主题
        "气候变化对中国城市的影响",    # 混合气候变化和城市主题
        "太空技术与人工智能的结合",    # 混合太空探索和AI主题
        "健康饮食与现代城市生活方式"   # 混合健康和城市生活主题
    ]
    
    for query in complex_queries:
        print(f"\n复杂查询: '{query}'")
        result = memory.get_memories_as_string(query)
        print(result)
        
    # 长文本记忆测试
    print("\n7. 长文本记忆测试")
    long_text = """
    智能城市是利用各种信息技术或创新概念，将城市的系统和服务连接起来，以提高资源利用效率，
    优化城市管理和服务，以及改善市民生活质量的城市发展模式。人工智能在智能城市中扮演着重要角色，
    例如智能交通系统可以利用AI分析交通流量，优化信号灯控制，减少拥堵；
    智能电网系统可以预测用电需求，平衡供需关系，提高能源利用效率；
    城市安全监控系统可以利用计算机视觉技术进行异常行为检测和预警。
    与此同时，随着气候变化的加剧，城市规划也需要考虑可持续发展因素，
    包括绿色建筑、可再生能源利用、以及应对极端天气的韧性设计等。
    未来城市的发展将更加注重人与自然的和谐共处，技术与人文的平衡融合。
    """
    
    print(f"\n添加长文本记忆: '{long_text[:50]}...'")
    memory.maintain_memory(long_text)
    
    long_text_queries = [
        "智能城市是什么",
        "人工智能在城市中的应用",
        "城市如何应对气候变化",
        "未来城市发展趋势"
    ]
    
    for query in long_text_queries:
        print(f"\n长文本相关查询: '{query}'")
        result = memory.get_memories_as_string(query)
        print(result)
    
    # 记忆图状态分析
    print("\n8. 记忆图状态分析")
    node_count = len(memory.memory_graph.nodes())
    edge_count = len(memory.memory_graph.edges())
    print(f"记忆图当前状态: {node_count} 个概念, {edge_count} 个连接")
    
    # 显示一些主要概念及其连接
    main_concepts = ["中国", "城市", "人工智能", "气候变化", "智能城市"]
    for concept in main_concepts:
        if concept in memory.memory_graph:
            neighbors = list(memory.memory_graph.neighbors(concept))
            print(f"\n概念 '{concept}' 的连接 ({len(neighbors)}):")
            for neighbor in sorted(neighbors)[:5]:  # 只显示前5个连接
                if neighbor in memory.memory_graph[concept]:
                    strength = memory.memory_graph[concept][neighbor].get("strength", 1)
                    print(f"- 连接到 '{neighbor}' (强度: {strength})")
    
    print("\n===== 演示结束 =====")

if __name__ == "__main__":
    demo() 