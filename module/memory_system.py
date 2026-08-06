import os
import json
import time
import datetime
import random
import math
import re
import hashlib
import logging
from typing import List, Dict, Set, Tuple, Optional, Any, Union
from collections import Counter
import networkx as nx
import numpy as np

try:
    import jieba
except ImportError:
    print("请安装jieba: pip install jieba")
    raise

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("SimpleMemory")


class SimpleMemory:
    """简化版记忆系统，模拟MaiBot的海马体记忆机制"""

    def __init__(self, 
                 memory_dir: str = "memory_data",
                 memory_file: str = "memory_graph.json",
                 memory_build_interval: int = 0,  # 降为0，禁用时间间隔检查
                 forget_interval: int = 1000,
                 consolidate_interval: int = 1000,
                 forget_time_hours: int = 24,
                 forget_percentage: float = 0.01,
                 consolidate_threshold: float = 0.7,
                 max_memory_per_node: int = 10,
                 debug: bool = False):  # 添加调试模式
        """初始化记忆系统
        
        Args:
            memory_dir: 记忆数据存储目录
            memory_file: 记忆图存储文件名
            memory_build_interval: 记忆构建间隔（秒）
            forget_interval: 记忆遗忘间隔（秒）
            consolidate_interval: 记忆整合间隔（秒）
            forget_time_hours: 记忆开始遗忘的时间（小时） 
            forget_percentage: 每次遗忘检查的节点比例
            consolidate_threshold: 记忆整合的相似度阈值
            max_memory_per_node: 每个节点最大记忆项数量
            debug: 是否启用调试模式
        """
        # 初始化记忆图
        self.memory_graph = nx.Graph()
        
        # 配置参数
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, memory_file)
        self.memory_build_interval = memory_build_interval
        self.forget_interval = forget_interval
        self.consolidate_interval = consolidate_interval
        self.forget_time_hours = forget_time_hours
        self.forget_percentage = forget_percentage
        self.consolidate_threshold = consolidate_threshold
        self.max_memory_per_node = max_memory_per_node
        self.debug = debug
        
        # 记忆禁用词
        self.memory_ban_words = ["表情包", "图片", "回复", "聊天记录"]
        
        # 时间记录
        self.last_build_time = 0
        self.last_forget_time = 0
        self.last_consolidate_time = 0
        
        # 确保记忆目录存在
        os.makedirs(memory_dir, exist_ok=True)
        
        # 加载现有记忆图（如果存在）
        self.load_memory_graph()
        
    def load_memory_graph(self):
        """从文件加载记忆图数据"""
        if not os.path.exists(self.memory_file):
            logger.info(f"记忆图文件不存在，创建新的记忆图: {self.memory_file}")
            return
            
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 重建图结构
            self.memory_graph = nx.Graph()
            
            # 添加节点
            for node, attrs in data["nodes"].items():
                self.memory_graph.add_node(
                    node,
                    memory_items=attrs.get("memory_items", []),
                    created_time=attrs.get("created_time", time.time()),
                    last_modified=attrs.get("last_modified", time.time())
                )
                
            # 添加边
            for edge in data["edges"]:
                self.memory_graph.add_edge(
                    edge["source"],
                    edge["target"],
                    strength=edge.get("strength", 1),
                    created_time=edge.get("created_time", time.time()),
                    last_modified=edge.get("last_modified", time.time())
                )
                
            logger.info(f"记忆图已加载: {len(self.memory_graph.nodes())} 个概念, {len(self.memory_graph.edges())} 个连接")
        except Exception as e:
            logger.error(f"加载记忆图失败: {e}")
            self.memory_graph = nx.Graph()
            
    def save_memory_graph(self):
        """保存记忆图到文件"""
        try:
            # 准备数据结构
            data = {
                "nodes": {},
                "edges": []
            }
            
            # 保存节点
            for node, attrs in self.memory_graph.nodes(data=True):
                data["nodes"][node] = {
                    "memory_items": attrs.get("memory_items", []),
                    "created_time": attrs.get("created_time", time.time()),
                    "last_modified": attrs.get("last_modified", time.time())
                }
                
            # 保存边
            for source, target, attrs in self.memory_graph.edges(data=True):
                data["edges"].append({
                    "source": source,
                    "target": target,
                    "strength": attrs.get("strength", 1),
                    "created_time": attrs.get("created_time", time.time()),
                    "last_modified": attrs.get("last_modified", time.time())
                })
                
            # 写入文件
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"记忆图已保存: {len(data['nodes'])} 个概念, {len(data['edges'])} 个连接")
        except Exception as e:
            logger.error(f"保存记忆图失败: {e}")
            
    def add_memory(self, concept: str, memory: str) -> bool:
        """添加记忆到指定概念
        
        Args:
            concept: 记忆概念
            memory: 记忆内容
            
        Returns:
            bool: 是否成功添加
        """
        if not concept or not memory:
            return False
            
        # 过滤禁用词
        if any(word in concept for word in self.memory_ban_words):
            logger.debug(f"概念含有禁用词，跳过: {concept}")
            return False
            
        current_time = time.time()
        
        # 检查节点是否存在
        if concept in self.memory_graph:
            # 获取现有记忆项
            if "memory_items" in self.memory_graph.nodes[concept]:
                memory_items = self.memory_graph.nodes[concept]["memory_items"]
                if not isinstance(memory_items, list):
                    memory_items = [memory_items]
                    
                # 避免重复记忆
                if memory in memory_items:
                    return False
                    
                # 限制每个节点的记忆数量
                if len(memory_items) >= self.max_memory_per_node:
                    # 移除最旧的记忆
                    memory_items.pop(0)
                    
                memory_items.append(memory)
                self.memory_graph.nodes[concept]["memory_items"] = memory_items
                self.memory_graph.nodes[concept]["last_modified"] = current_time
            else:
                self.memory_graph.nodes[concept]["memory_items"] = [memory]
                self.memory_graph.nodes[concept]["last_modified"] = current_time
                
            logger.debug(f"向现有概念添加记忆: {concept}")
        else:
            # 创建新节点
            self.memory_graph.add_node(
                concept,
                memory_items=[memory],
                created_time=current_time,
                last_modified=current_time
            )
            logger.debug(f"创建新概念: {concept}")
            
        return True
        
    def connect_concepts(self, concept1: str, concept2: str, strength: int = None) -> bool:
        """连接两个概念
        
        Args:
            concept1: 第一个概念
            concept2: 第二个概念
            strength: 连接强度，如果为None则根据相似度计算
            
        Returns:
            bool: 是否成功连接
        """
        if concept1 == concept2:
            return False
            
        if concept1 not in self.memory_graph or concept2 not in self.memory_graph:
            return False
            
        current_time = time.time()
        
        # 如果未提供强度，计算概念相似度作为强度
        if strength is None:
            similarity = self._calculate_concept_similarity(concept1, concept2)
            strength = max(1, int(similarity * 10))
            
        # 检查边是否存在
        if self.memory_graph.has_edge(concept1, concept2):
            # 增加连接强度
            self.memory_graph[concept1][concept2]["strength"] += 1
            self.memory_graph[concept1][concept2]["last_modified"] = current_time
        else:
            # 创建新连接
            self.memory_graph.add_edge(
                concept1,
                concept2,
                strength=strength,
                created_time=current_time,
                last_modified=current_time
            )
            logger.debug(f"连接概念: {concept1} <-> {concept2} (强度: {strength})")
            
        return True
        
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """从文本中提取主题
        
        Args:
            text: 输入文本
            max_topics: 最大主题数量
            
        Returns:
            List[str]: 提取的主题列表
        """
        if not text:
            return []
            
        # 使用jieba分词提取关键词
        words = list(jieba.cut(text))
        
        # 过滤单字词和停用词
        filtered_words = [w for w in words if len(w) > 1 and not w.isdigit() and w not in self.memory_ban_words]
        
        # 计算词频
        word_counts = Counter(filtered_words)
        
        # 选取前N个高频词作为主题
        topics = [word for word, _ in word_counts.most_common(max_topics)]
        
        if self.debug:
            logger.debug(f"从文本提取主题: {topics}, 原始文本: {text[:50]}...")
            
        return topics
        
    def summarize_topic(self, text: str, topic: str) -> str:
        """为主题生成摘要
        
        Args:
            text: 输入文本
            topic: 主题
            
        Returns:
            str: 主题摘要
        """
        if not text or not topic:
            return ""
            
        # 找出包含主题的句子
        sentences = re.split(r'[。！？.!?]', text)
        relevant_sentences = [s for s in sentences if topic in s]
        
        if not relevant_sentences:
            # 如果没有直接包含主题的句子，取前1-2个句子
            summary = " ".join(sentences[:2])
        else:
            # 取最相关的1-2个句子
            summary = " ".join(relevant_sentences[:2])
            
        # 确保摘要长度适中
        if len(summary) > 200:
            summary = summary[:197] + "..."
            
        return summary
        
    def build_memory_from_text(self, text: str) -> int:
        """从文本构建记忆
        
        Args:
            text: 输入文本
            
        Returns:
            int: 添加的记忆数量
        """
        if not text:
            return 0
            
        current_time = time.time()
        self.last_build_time = current_time
        
        # 提取主题
        topics = self.extract_topics(text)
        if not topics:
            if self.debug:
                logger.debug("没有从文本中提取到主题")
            return 0
            
        # 添加记忆
        memory_count = 0
        new_topics = []
        
        for topic in topics:
            # 为主题生成摘要
            summary = self.summarize_topic(text, topic)
            if not summary:
                if self.debug:
                    logger.debug(f"主题 '{topic}' 没有生成摘要")
                continue
                
            # 添加记忆
            if self.add_memory(topic, summary):
                memory_count += 1
                new_topics.append(topic)
                if self.debug:
                    logger.debug(f"添加记忆: '{topic}' -> '{summary[:30]}...'")
            else:
                if self.debug:
                    logger.debug(f"未能添加记忆: '{topic}'")
                
        # 连接相关主题
        for i in range(len(new_topics)):
            for j in range(i+1, len(new_topics)):
                if self.connect_concepts(new_topics[i], new_topics[j]):
                    if self.debug:
                        logger.debug(f"连接概念: '{new_topics[i]}' <-> '{new_topics[j]}'")
                
        # 查找与现有概念的相似关系
        for topic in new_topics:
            similar_concepts = self._find_similar_concepts(topic, threshold=0.7)
            for concept, similarity in similar_concepts:
                strength = max(1, int(similarity * 10))
                if self.connect_concepts(topic, concept, strength):
                    if self.debug:
                        logger.debug(f"连接相似概念: '{topic}' <-> '{concept}' (相似度: {similarity:.2f})")
                
        # 保存记忆图
        self.save_memory_graph()
        
        return memory_count
        
    def check_and_build_memory(self, text: str = None) -> int:
        """检查是否需要构建记忆，如果需要则构建
        
        Args:
            text: 输入文本，如果为None则不构建
            
        Returns:
            int: 添加的记忆数量
        """
        current_time = time.time()
        
        # 检查是否到构建时间，memory_build_interval为0时跳过时间检查
        if self.memory_build_interval > 0 and current_time - self.last_build_time < self.memory_build_interval:
            if self.debug:
                logger.debug("未到记忆构建时间，跳过构建")
            return 0
            
        if text:
            return self.build_memory_from_text(text)
        return 0
        
    def forget_memory(self) -> int:
        """执行记忆遗忘操作
        
        Returns:
            int: 遗忘的记忆数量
        """
        current_time = time.time()
        
        # 如果未到遗忘时间，则跳过
        if current_time - self.last_forget_time < self.forget_interval:
            return 0
            
        self.last_forget_time = current_time
        forget_time_seconds = self.forget_time_hours * 3600
        forgotten_count = 0
        
        all_nodes = list(self.memory_graph.nodes())
        
        # 如果没有节点，直接返回
        if not all_nodes:
            return 0
            
        # 确定要检查的节点数量
        check_count = max(1, int(len(all_nodes) * self.forget_percentage))
        nodes_to_check = random.sample(all_nodes, min(check_count, len(all_nodes)))
        
        nodes_to_remove = []
        
        for node in nodes_to_check:
            node_data = self.memory_graph.nodes[node]
            
            # 检查节点是否已足够老
            if "created_time" in node_data:
                node_age = current_time - node_data["created_time"]
                
                # 如果节点太新，跳过
                if node_age < forget_time_seconds:
                    continue
                    
            # 获取记忆项
            memory_items = node_data.get("memory_items", [])
            if not isinstance(memory_items, list):
                memory_items = [memory_items]
                
            # 如果没有记忆项，标记节点删除
            if not memory_items:
                nodes_to_remove.append(node)
                continue
                
            # 获取连接数
            connections = list(self.memory_graph.neighbors(node))
            connection_count = len(connections)
            
            # 计算遗忘概率 - 连接越多越不容易遗忘
            base_forget_prob = 0.3
            adjusted_prob = base_forget_prob / (1 + 0.1 * connection_count)
            
            # 随机决定是否遗忘
            if random.random() < adjusted_prob:
                if len(memory_items) > 1:
                    # 随机移除一个记忆项
                    removed_item = random.choice(memory_items)
                    memory_items.remove(removed_item)
                    self.memory_graph.nodes[node]["memory_items"] = memory_items
                    logger.debug(f"从概念 '{node}' 遗忘一条记忆")
                    forgotten_count += 1
                else:
                    # 只有一个记忆项，标记整个节点删除
                    nodes_to_remove.append(node)
                    forgotten_count += 1
        
        # 移除标记的节点
        for node in nodes_to_remove:
            self.memory_graph.remove_node(node)
            logger.debug(f"遗忘概念: {node}")
            
        # 保存记忆图
        self.save_memory_graph()
        
        return forgotten_count
        
    def consolidate_memory(self) -> int:
        """整合相似记忆
        
        Returns:
            int: 整合的记忆数量
        """
        current_time = time.time()
        
        # 如果未到整合时间，则跳过
        if current_time - self.last_consolidate_time < self.consolidate_interval:
            return 0
            
        self.last_consolidate_time = current_time
        consolidated_count = 0
        
        all_nodes = list(self.memory_graph.nodes())
        
        # 如果没有节点，直接返回
        if not all_nodes:
            return 0
            
        # 确定要检查的节点数量
        check_count = max(1, int(len(all_nodes) * self.forget_percentage))
        nodes_to_check = random.sample(all_nodes, min(check_count, len(all_nodes)))
        
        for node in nodes_to_check:
            node_data = self.memory_graph.nodes[node]
            
            # 获取记忆项
            memory_items = node_data.get("memory_items", [])
            if not isinstance(memory_items, list):
                memory_items = [memory_items]
                
            # 如果记忆项少于2个，跳过
            if len(memory_items) < 2:
                continue
                
            # 检查所有记忆项对的相似度
            consolidated = False
            items_copy = memory_items.copy()
            
            for i in range(len(items_copy)):
                if consolidated:
                    break
                    
                for j in range(i + 1, len(items_copy)):
                    item1 = items_copy[i]
                    item2 = items_copy[j]
                    
                    # 计算相似度
                    similarity = self._calculate_text_similarity(item1, item2)
                    
                    if similarity >= self.consolidate_threshold:
                        # 计算信息量
                        info1 = self._calculate_information_content(item1)
                        info2 = self._calculate_information_content(item2)
                        
                        # 保留信息量更高的记忆
                        if info1 >= info2:
                            # 移除item2
                            memory_items.remove(item2)
                        else:
                            # 移除item1
                            memory_items.remove(item1)
                            
                        # 更新节点数据
                        self.memory_graph.nodes[node]["memory_items"] = memory_items
                        self.memory_graph.nodes[node]["last_modified"] = current_time
                        
                        consolidated = True
                        consolidated_count += 1
                        logger.debug(f"整合概念 '{node}' 中的相似记忆")
                        break
        
        # 保存记忆图
        if consolidated_count > 0:
            self.save_memory_graph()
            
        return consolidated_count
        
    def get_memories_from_text(self, text: str, max_memories: int = 3) -> List[Dict[str, Any]]:
        """从输入文本获取相关记忆
        
        Args:
            text: 输入文本
            max_memories: 最大返回记忆数量
            
        Returns:
            List[Dict[str, Any]]: 记忆列表，每项包含主题、记忆内容和相关度
        """
        if not text or not self.memory_graph.nodes:
            if self.debug:
                logger.debug("记忆图为空或查询文本为空")
            return []
            
        # 提取关键词
        keywords = self.extract_topics(text)
        if not keywords:
            if self.debug:
                logger.debug(f"从查询文本中没有提取到关键词: {text}")
            return []
            
        # 计算关键词的IDF值
        idf_values = self._calculate_idf_values(keywords)
        if self.debug:
            logger.debug(f"查询关键词IDF值: {idf_values}")
            
        # 找出有效关键词（存在于记忆图中的）
        valid_keywords = [k for k in keywords if k in self.memory_graph]
        if not valid_keywords:
            if self.debug:
                logger.debug(f"没有关键词存在于记忆图中: {keywords}")
            
            # 尝试查找相似的概念
            similar_concepts = []
            for keyword in keywords:
                similar = self._find_similar_concepts(keyword, threshold=0.5)
                similar_concepts.extend([c for c, _ in similar])
            
            if similar_concepts:
                if self.debug:
                    logger.debug(f"找到相似概念: {similar_concepts}")
                valid_keywords = similar_concepts
            else:
                return []
            
        # 计算激活值
        activation_values = {}
        
        # 对每个关键词进行激活扩散
        for keyword in valid_keywords:
            # 获取关键词的IDF值，赋予更高的初始激活值给罕见词
            keyword_idf = idf_values.get(keyword, 1.0)
            initial_activation = 1.0 * keyword_idf  # IDF值越高，初始激活值越高
            
            if self.debug:
                logger.debug(f"关键词 '{keyword}' 初始激活值: {initial_activation} (IDF: {keyword_idf})")
            
            # 初始化激活值
            current_activation = {keyword: initial_activation}
            visited = {keyword}
            
            # 待处理队列：(节点, 激活值, 深度)
            queue = [(keyword, initial_activation, 0)]
            max_depth = 3  # 最大扩散深度
            
            while queue:
                current_node, activation, depth = queue.pop(0)
                
                # 如果超过最大深度，停止扩散
                if depth >= max_depth:
                    continue
                    
                # 获取邻居节点
                if current_node in self.memory_graph:
                    neighbors = list(self.memory_graph.neighbors(current_node))
                else:
                    # 节点可能在扩散过程中被其他进程删除
                    continue
                
                for neighbor in neighbors:
                    if neighbor in visited:
                        continue
                        
                    # 获取连接强度
                    edge_data = self.memory_graph[current_node][neighbor]
                    strength = edge_data.get("strength", 1)
                    
                    # 计算新激活值，考虑IDF因子
                    neighbor_idf = idf_values.get(neighbor, 1.0)
                    decay_factor = 1 / strength
                    new_activation = activation - decay_factor
                    
                    # 根据IDF调整扩散激活值
                    new_activation = new_activation * neighbor_idf
                    
                    if new_activation > 0:
                        # 更新激活值
                        current_activation[neighbor] = new_activation
                        visited.add(neighbor)
                        queue.append((neighbor, new_activation, depth + 1))
                        
                        if self.debug and depth < 2:  # 只记录前两层的扩散，避免日志过多
                            logger.debug(f"激活扩散: '{current_node}' -> '{neighbor}' = {new_activation:.2f}")
            
            # 更新全局激活映射
            for node, value in current_activation.items():
                if node in activation_values:
                    activation_values[node] += value
                else:
                    activation_values[node] = value
        
        # 根据激活值选择记忆
        results = []
        
        # 按激活值排序
        sorted_activations = sorted(activation_values.items(), key=lambda x: x[1], reverse=True)
        
        if self.debug:
            top_activations = sorted_activations[:min(5, len(sorted_activations))]
            logger.debug(f"激活值排序 (Top 5): {[(c, round(v, 2)) for c, v in top_activations]}")
        
        # 选择最相关的节点
        for concept, activation in sorted_activations[:max_memories]:
            # 获取节点记忆
            if concept in self.memory_graph:
                node_data = self.memory_graph.nodes[concept]
                memory_items = node_data.get("memory_items", [])
                
                if not memory_items:
                    if self.debug:
                        logger.debug(f"概念 '{concept}' 没有记忆项")
                    continue
                    
                if not isinstance(memory_items, list):
                    memory_items = [memory_items]
                    
                # 选择最近的记忆
                memory = memory_items[-1]
                
                results.append({
                    "topic": concept,
                    "content": memory,
                    "relevance": activation
                })
                
                if self.debug:
                    logger.debug(f"返回记忆: '{concept}' (相关度: {activation:.2f})")
            
        return results
        
    def get_memories_as_string(self, text: str, max_memories: int = 3) -> str:
        """从文本获取相关记忆，以字符串形式返回
        
        Args:
            text: 输入文本
            max_memories: 最大返回记忆数量
            
        Returns:
            str: 格式化的记忆字符串
        """
        # 直接获取相关记忆，不进行记忆维护
        memories = self.get_memories_from_text(text, max_memories)
        
        if not memories:
            return "没有找到相关记忆。"
            
        # 格式化记忆
        result = "相关记忆：\n\n"
        for i, memory in enumerate(memories, 1):
            result += f"{i}. 关于「{memory['topic']}」：{memory['content']}\n\n"
            
        return result.strip()
        
    def maintain_memory(self, text: str = None) -> Dict[str, int]:
        """维护记忆系统，执行构建、遗忘和整合操作
        
        Args:
            text: 可选的输入文本，用于构建新记忆
            
        Returns:
            Dict[str, int]: 维护操作的结果统计
        """
        result = {
            "built": 0,
            "forgotten": 0,
            "consolidated": 0
        }
        
        # 构建新记忆 - 直接调用build_memory_from_text，跳过时间间隔检查
        if text:
            result["built"] = self.build_memory_from_text(text)
            if self.debug:
                logger.debug(f"维护记忆: 添加了 {result['built']} 个新记忆")
            
        # 执行记忆遗忘
        result["forgotten"] = self.forget_memory()
        if self.debug and result["forgotten"] > 0:
            logger.debug(f"维护记忆: 遗忘了 {result['forgotten']} 个记忆")
        
        # 执行记忆整合
        result["consolidated"] = self.consolidate_memory()
        if self.debug and result["consolidated"] > 0:
            logger.debug(f"维护记忆: 整合了 {result['consolidated']} 个记忆")
        
        return result
    
    def _calculate_idf_values(self, keywords: List[str]) -> Dict[str, float]:
        """计算关键词的IDF值
        
        Args:
            keywords: 关键词列表
            
        Returns:
            Dict[str, float]: 关键词IDF值映射
        """
        # 获取记忆图中的总节点数
        total_nodes = len(self.memory_graph.nodes())
        if total_nodes == 0:
            return {keyword: 1.0 for keyword in keywords}
            
        idf_values = {}
        
        for keyword in keywords:
            # 计算包含该关键词的节点数
            # 这里简化为仅检查节点名称是否包含该词，也可以扩展为检查节点的记忆内容
            containing_nodes = sum(1 for node in self.memory_graph.nodes() if keyword in node)
            
            # 避免除零错误
            if containing_nodes == 0:
                containing_nodes = 1
                
            # 计算IDF值: log(总节点数/包含该词的节点数)
            idf = math.log(total_nodes / containing_nodes)
            
            # 归一化，确保IDF在合理范围内
            idf = min(3.0, max(0.5, idf))
            
            idf_values[keyword] = idf
            
        return idf_values
        
    def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """计算两个概念的相似度，使用TF-IDF加权
        
        Args:
            concept1: 第一个概念
            concept2: 第二个概念
            
        Returns:
            float: 相似度 (0-1)
        """
        # 分词
        words1 = list(jieba.cut(concept1))
        words2 = list(jieba.cut(concept2))
        
        # 计算词频 (TF)
        tf1 = Counter(words1)
        tf2 = Counter(words2)
        
        # 构建词汇并集
        all_words = set(words1) | set(words2)
        
        # 计算IDF值
        idf_values = self._calculate_idf_values(list(all_words))
        
        # 构建TF-IDF加权向量
        v1 = []
        v2 = []
        
        for word in all_words:
            # 获取TF值
            tf1_val = tf1.get(word, 0) / max(len(words1), 1)
            tf2_val = tf2.get(word, 0) / max(len(words2), 1)
            
            # 获取IDF值
            idf = idf_values.get(word, 1.0)
            
            # 计算TF-IDF值
            v1.append(tf1_val * idf)
            v2.append(tf2_val * idf)
        
        # 计算余弦相似度
        return self._cosine_similarity(v1, v2)
        
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度，使用TF-IDF加权
        
        Args:
            text1: 第一段文本
            text2: 第二段文本
            
        Returns:
            float: 相似度 (0-1)
        """
        # 分词
        words1 = list(jieba.cut(text1))
        words2 = list(jieba.cut(text2))
        
        # 计算词频 (TF)
        tf1 = Counter(words1)
        tf2 = Counter(words2)
        
        # 构建词汇并集
        all_words = set(words1) | set(words2)
        
        # 计算IDF值
        idf_values = self._calculate_idf_values(list(all_words))
        
        # 构建TF-IDF加权向量
        v1 = []
        v2 = []
        
        for word in all_words:
            # 获取TF值
            tf1_val = tf1.get(word, 0) / max(len(words1), 1)
            tf2_val = tf2.get(word, 0) / max(len(words2), 1)
            
            # 获取IDF值
            idf = idf_values.get(word, 1.0)
            
            # 计算TF-IDF值
            v1.append(tf1_val * idf)
            v2.append(tf2_val * idf)
        
        # 计算余弦相似度
        return self._cosine_similarity(v1, v2)
        
    def _cosine_similarity(self, v1: List[int], v2: List[int]) -> float:
        """计算余弦相似度
        
        Args:
            v1: 第一个向量
            v2: 第二个向量
            
        Returns:
            float: 相似度 (0-1)
        """
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return dot_product / (norm1 * norm2)
        
    def _calculate_information_content(self, text: str) -> float:
        """计算文本的信息熵
        
        Args:
            text: 输入文本
            
        Returns:
            float: 信息熵
        """
        # 计算字符频率
        char_count = Counter(text)
        total_chars = len(text)
        
        if total_chars == 0:
            return 0
            
        # 计算熵
        entropy = 0
        for count in char_count.values():
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
            
        return entropy
        
    def _find_similar_concepts(self, concept: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """找出与指定概念相似的概念
        
        Args:
            concept: 概念
            threshold: 相似度阈值
            
        Returns:
            List[Tuple[str, float]]: 相似概念列表，每项为(概念, 相似度)
        """
        similar_concepts = []
        
        for node in self.memory_graph.nodes():
            if node == concept:
                continue
                
            similarity = self._calculate_concept_similarity(concept, node)
            if similarity >= threshold:
                similar_concepts.append((node, similarity))
                
        # 按相似度降序排序
        similar_concepts.sort(key=lambda x: x[1], reverse=True)
        
        return similar_concepts[:3]  # 返回最相似的3个概念


# 用法示例
if __name__ == "__main__":
    # 创建记忆系统实例
    memory = SimpleMemory()
    
    # 添加一些初始记忆
    sample_text1 = "北京是中国的首都，有着悠久的历史和丰富的文化遗产。长城是中国古代伟大的防御工程，也是世界文化遗产。"
    sample_text2 = "上海是中国最大的城市，是重要的经济、金融中心。上海的外滩有许多历史建筑，是著名的旅游景点。"
    sample_text3 = "人工智能技术正在迅速发展，包括机器学习、深度学习等多个领域。GPT是一种基于Transformer架构的大型语言模型。"
    
    memory.build_memory_from_text(sample_text1)
    memory.build_memory_from_text(sample_text2)
    memory.build_memory_from_text(sample_text3)
    
    # 检索相关记忆
    query = "我想了解中国的城市"
    result = memory.get_memories_as_string(query)
    print(result) 