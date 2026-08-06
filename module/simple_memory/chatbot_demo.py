#!/usr/bin/env python
# -*- coding: utf-8 -*-

from memory_system import SimpleMemory
import time
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ChatbotDemo")

class SimpleChat:
    """简单聊天机器人，集成记忆系统"""
    
    def __init__(self):
        """初始化聊天机器人"""
        self.memory = SimpleMemory(
            memory_dir="chat_memory_data",
            memory_build_interval=30,      # 30秒构建一次记忆
            forget_interval=300,           # 5分钟执行一次遗忘
            consolidate_interval=600,      # 10分钟执行一次整合
            forget_time_hours=1,           # 1小时后记忆可以被遗忘
            forget_percentage=0.1,         # 每次检查10%的节点
            max_memory_per_node=15         # 每个概念最多保存15条记忆
        )
        
        # 历史消息
        self.history = []
        
        # 预设回复模板（简化版）
        self.templates = {
            "greeting": [
                "你好！很高兴与你交流。",
                "嗨，我是一个集成了记忆系统的聊天机器人，有什么可以帮到你的吗？",
                "欢迎！我可以记住我们的对话，有什么想聊的吗？"
            ],
            "farewell": [
                "再见，期待下次与你交流！",
                "下次再聊，祝你一天愉快！",
                "再会，感谢与你交谈！"
            ],
            "unknown": [
                "抱歉，我不太理解你的意思。",
                "这个问题有点复杂，能否换个方式表达？",
                "嗯，这个话题我不太熟悉。"
            ],
            "memory_transition": [
                "这让我想起了...",
                "我记得关于这个话题...",
                "根据我的记忆...",
                "之前我们讨论过相关内容..."
            ]
        }
        
        # 关键词触发器
        self.keyword_triggers = {
            "你好": "greeting",
            "嗨": "greeting",
            "再见": "farewell",
            "拜拜": "farewell"
        }
        
    def get_response(self, user_input: str) -> str:
        """根据用户输入生成回复
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            str: 机器人回复
        """
        if not user_input.strip():
            return "你似乎没有说什么..."
        
        # 记录用户输入到历史
        self.history.append({"role": "user", "content": user_input})
        
        # 检查关键词触发器
        for keyword, template_key in self.keyword_triggers.items():
            if keyword in user_input:
                response = random.choice(self.templates[template_key])
                self.history.append({"role": "bot", "content": response})
                return response
        
        # 尝试从记忆中获取相关内容
        memories = self.memory.get_memories_from_text(user_input, max_memories=2)
        
        # 检查是否触发记忆构建
        self.memory.check_and_build_memory(user_input)
        # 检查是否触发记忆维护（遗忘和整合）
        self.memory.forget_memory()
        self.memory.consolidate_memory()
        
        if memories:
            # 基于记忆生成回复
            memory_transition = random.choice(self.templates["memory_transition"])
            memory_content = memories[0]["content"]
            topic = memories[0]["topic"]
            
            response = f"{memory_transition} {memory_content}"
            
            # 如果回复太短，可以添加更多上下文
            if len(memories) > 1 and len(response) < 100:
                response += f"\n\n另外，关于{memories[1]['topic']}，我记得: {memories[1]['content']}"
                
            # 保存机器人回复到历史记录
            self.history.append({"role": "bot", "content": response})
            
            # 构建记忆（记住机器人自己的回复）
            memory_text = f"用户询问了关于{topic}的信息，我告诉了他：{response}"
            self.memory.check_and_build_memory(memory_text)
            
            return response
        else:
            # 没有找到相关记忆，使用通用回复
            response = random.choice(self.templates["unknown"])
            self.history.append({"role": "bot", "content": response})
            return response
    
    def chat_loop(self):
        """启动交互式聊天循环"""
        print("=== 记忆型聊天机器人演示 ===")
        print("输入'退出'或'exit'结束对话\n")
        
        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ["退出", "exit", "quit", "bye"]:
                print(f"\n机器人: {random.choice(self.templates['farewell'])}")
                break
                
            response = self.get_response(user_input)
            print(f"\n机器人: {response}")
            
            # 打印当前记忆节点数量
            node_count = len(self.memory.memory_graph.nodes())
            edge_count = len(self.memory.memory_graph.edges())
            print(f"\n[记忆状态: {node_count}个概念, {edge_count}个连接]")


def main():
    # 添加一些初始知识
    chatbot = SimpleChat()
    
    # 预填充一些知识
    initial_knowledge = [
        "Python是一种高级编程语言，以其简洁、易读的语法著称。Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。",
        "机器学习是人工智能的一个子领域，主要研究如何让计算机不通过明确编程而自主学习。机器学习算法通常基于样本数据（训练集）来进行预测或决策。",
        "自然语言处理(NLP)是计算机科学和人工智能的一个子领域，专注于让计算机理解、解释和生成人类语言。它结合了计算语言学、统计学和机器学习方法。",
        "记忆系统在AI中非常重要，可以帮助模型保持上下文连贯性和记住过去的交互。这对于构建更自然的对话系统至关重要。",
        "图结构是一种由节点和连接节点的边组成的数据结构。在计算机科学中，图被广泛应用于表示网络、关系和路径等。"
    ]
    
    for knowledge in initial_knowledge:
        chatbot.memory.build_memory_from_text(knowledge)
    
    print(f"已预加载 {len(initial_knowledge)} 条知识")
    
    # 启动聊天循环
    chatbot.chat_loop()


if __name__ == "__main__":
    main() 