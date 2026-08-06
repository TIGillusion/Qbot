#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_memory.memory_system import SimpleMemory

def add_memory(memory_text, memory_path="memory_data"):
    """
    添加记忆到记忆系统
    
    Args:
        memory_text (str): 需要记住的文本内容
        memory_path (str): 记忆数据存储路径
    
    Returns:
        dict: 包含添加结果的字典，键 'built' 表示新添加的记忆数量
    """
    # 初始化记忆系统，禁用时间间隔检查
    memory = SimpleMemory(memory_dir=memory_path, memory_build_interval=0)
    
    # 添加记忆
    result = memory.maintain_memory(memory_text)
    
    return result

def query_memory(query_text, memory_path="memory_data"):
    """
    从记忆系统中查询相关记忆
    
    Args:
        query_text (str): 查询文本
        memory_path (str): 记忆数据存储路径
    
    Returns:
        str: 与查询相关的记忆内容
    """
    # 初始化记忆系统
    memory = SimpleMemory(memory_dir=memory_path)
    
    # 查询记忆
    result = memory.get_memories_as_string(query_text)
    
    return result 

def forget_memory(memory_path="memory_data", forget_percentage=0.01, forget_time_hours=24, 
                 forget_mode="random", importance_threshold=None, connection_threshold=None):
    """
    执行记忆遗忘操作，根据不同策略遗忘部分记忆
    
    Args:
        memory_path (str): 记忆数据存储路径
        forget_percentage (float): 每次检查的记忆节点比例，范围0-1
        forget_time_hours (int): 记忆需要存在多久才会被考虑遗忘（小时）
        forget_mode (str): 遗忘模式，可选值：
            - "random": 随机遗忘 (默认)
            - "least_connected": 优先遗忘连接较少的概念
            - "least_recent": 优先遗忘最近未使用的概念
            - "least_important": 优先遗忘重要性较低的概念
        importance_threshold (float): 重要性阈值，低于此值的概念更容易被遗忘
        connection_threshold (int): 连接数阈值，连接数低于此值的概念更容易被遗忘
    
    Returns:
        int: 遗忘的记忆数量
    """
    # 初始化记忆系统，设置遗忘参数
    memory = SimpleMemory(
        memory_dir=memory_path, 
        forget_percentage=forget_percentage,
        forget_time_hours=forget_time_hours,
        forget_interval=0  # 禁用时间间隔检查，确保立即执行遗忘
    )
    
    # 获取记忆图
    memory_graph = memory.memory_graph
    
    # 根据不同的遗忘模式调整遗忘策略
    if forget_mode != "random" and memory_graph.nodes():
        all_nodes = list(memory_graph.nodes())
        
        # 确定要检查的节点数量
        check_count = max(1, int(len(all_nodes) * forget_percentage))
        
        if forget_mode == "least_connected":
            # 按连接数排序节点
            nodes_by_connections = sorted(
                [(node, len(list(memory_graph.neighbors(node)))) for node in all_nodes],
                key=lambda x: x[1]
            )
            # 选择连接最少的节点进行检查
            nodes_to_check = [node for node, _ in nodes_by_connections[:check_count]]
            
            # 如果设置了连接阈值，调整遗忘概率
            if connection_threshold is not None:
                # 修改记忆系统的遗忘算法参数
                memory.forget_connection_threshold = connection_threshold
                
        elif forget_mode == "least_recent":
            # 按最后修改时间排序节点
            nodes_by_recency = sorted(
                [(node, memory_graph.nodes[node].get("last_modified", 0)) for node in all_nodes],
                key=lambda x: x[1]
            )
            # 选择最旧的节点进行检查
            nodes_to_check = [node for node, _ in nodes_by_recency[:check_count]]
            
        elif forget_mode == "least_important":
            # 计算节点的重要性（基于连接数和连接强度）
            node_importance = []
            for node in all_nodes:
                connections = list(memory_graph.neighbors(node))
                connection_count = len(connections)
                
                # 计算连接强度总和
                strength_sum = 0
                for neighbor in connections:
                    if node in memory_graph and neighbor in memory_graph[node]:
                        strength_sum += memory_graph[node][neighbor].get("strength", 1)
                
                # 重要性 = 连接数 * 平均连接强度
                avg_strength = strength_sum / max(1, connection_count)
                importance = connection_count * avg_strength
                
                node_importance.append((node, importance))
            
            # 按重要性排序
            node_importance.sort(key=lambda x: x[1])
            
            # 选择重要性最低的节点进行检查
            nodes_to_check = [node for node, _ in node_importance[:check_count]]
            
            # 如果设置了重要性阈值，调整遗忘概率
            if importance_threshold is not None:
                # 修改记忆系统的遗忘算法参数
                memory.forget_importance_threshold = importance_threshold
        
        # 设置要检查的节点
        memory.nodes_to_check = nodes_to_check
    
    # 执行遗忘操作
    forgotten_count = memory.forget_memory()
    
    return forgotten_count 