#!/usr/bin/env python
# -*- coding: utf-8 -*-

from memory_system import SimpleMemory
import time
import logging
import os
import random
import json
from datetime import datetime

# 设置日志级别
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MemoryLargeTest")

class MemorySystemEvaluator:
    """记忆系统大规模测试和评估工具"""
    
    def __init__(self, memory_dir="large_test_memory", clean_start=True):
        """初始化评估器
        
        Args:
            memory_dir: 记忆存储目录
            clean_start: 是否清除旧的记忆数据
        """
        self.memory_dir = memory_dir
        self.results_log = []
        self.start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"memory_test_{self.start_time}.log"
        
        # 清理旧的测试记忆（如果需要）
        if clean_start and os.path.exists(os.path.join(memory_dir, "memory_graph.json")):
            os.remove(os.path.join(memory_dir, "memory_graph.json"))
            
        # 创建记忆系统实例
        self.memory = SimpleMemory(
            memory_dir=memory_dir, 
            memory_build_interval=0,  # 禁用时间间隔检查
            debug=False  # 生产模式关闭调试输出
        )
        
        # 确保记忆目录存在
        os.makedirs(memory_dir, exist_ok=True)
        
    def log(self, message):
        """记录消息到日志和控制台"""
        print(message)
        self.results_log.append(message)
        
    def save_results(self):
        """保存测试结果到文件"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.results_log))
        self.log(f"测试结果已保存到 {self.log_file}")
        
    def load_memory_samples(self, category, num_samples=None):
        """加载指定类别的记忆样本
        
        Args:
            category: 样本类别
            num_samples: 加载的样本数量，None表示全部
            
        Returns:
            list: 记忆样本列表
        """
        samples = {
            "科技": [
                "人工智能是计算机科学的一个重要领域，致力于创造能够模拟人类智能的计算机系统。深度学习是人工智能的一个分支，使用多层神经网络进行学习。",
                "区块链是一种分布式账本技术，它允许数据块以安全、不可篡改的方式被记录下来。比特币是第一个基于区块链技术的加密货币。",
                "量子计算是利用量子力学现象（如叠加和纠缠）进行计算的技术。量子计算机有望解决传统计算机难以处理的复杂问题。",
                "5G是第五代移动通信技术，提供更快的数据传输速度、更低的延迟和更大的网络容量。它将推动物联网和智能城市的发展。",
                "虚拟现实(VR)技术创造了一个完全沉浸式的数字环境，而增强现实(AR)则是将数字信息叠加到物理世界上。这些技术正在改变我们的娱乐和工作方式。",
                "机器学习是人工智能的一个子领域，它使用统计方法使计算机系统能够从数据中学习，而不是通过明确编程来执行任务。",
                "自然语言处理是计算机科学和人工智能的一个领域，致力于让计算机理解、解释和生成人类语言。GPT和BERT是近年来NLP领域的重大突破。",
                "大数据技术指的是处理和分析超出传统数据处理软件能力范围的大量复杂数据的技术。大数据的特点包括数据量大、多样性和速度快。",
                "边缘计算是一种分布式计算架构，将数据处理从中心化的云计算设施转移到更靠近数据源的\"边缘\"。这减少了延迟，提高了实时处理能力。"
            ],
            "城市": [
                "北京是中国的首都，拥有近3000年的历史和丰富的文化遗产。故宫和长城是北京最著名的历史遗迹，吸引着世界各地的游客。",
                "上海是中国最大的城市和全球金融中心之一，位于长江入海口。上海的外滩是著名的旅游景点，汇集了各种建筑风格的历史建筑。",
                "深圳是中国改革开放的窗口，从一个小渔村发展成为现代化大都市。深圳是全球重要的电子产品制造中心和创新科技中心。",
                "杭州是浙江省省会，以西湖风景和悠久的历史文化而闻名。它也是电子商务巨头阿里巴巴的总部所在地。",
                "成都是四川省省会，以美食和休闲生活方式而闻名。它是中国西部地区重要的经济中心，也是大熊猫的故乡。",
                "广州是广东省省会，有着2200多年的历史，是中国南部最重要的商业和贸易中心。广州美食在全球享有盛誉。",
                "重庆是中国中西部地区最大的城市，以其独特的山城地貌和火锅而闻名。长江和嘉陵江在此交汇，形成壮观的两江交汇景观。",
                "西安是中国四大古都之一，拥有丰富的历史遗迹，包括世界闻名的兵马俑和古城墙。它是古丝绸之路的起点。",
                "南京是江苏省省会，有着悠久的历史，曾多次作为中国的首都。中山陵和明孝陵是南京著名的历史景点。",
                "武汉是湖北省省会，位于长江中游，由武昌、汉口和汉阳三个历史城区组成。它是中国中部地区最重要的经济中心。"
            ],
            "环境": [
                "气候变化是当今世界面临的最严峻挑战之一，全球变暖导致极端天气事件增多，如热浪、干旱和洪水等。减少碳排放是应对气候变化的关键。",
                "可再生能源包括太阳能、风能、水能等，是替代化石燃料的清洁能源。发展可再生能源是实现碳中和目标的重要途径。",
                "生物多样性指地球上所有生物的多样性，包括物种、基因和生态系统的多样性。人类活动导致生物多样性急剧下降，威胁生态平衡。",
                "水资源危机是全球面临的严重问题，包括淡水短缺、水污染和水资源分配不均。保护水源和提高用水效率至关重要。",
                "森林砍伐不仅减少了地球的绿色覆盖，还导致野生动物栖息地丧失和温室气体排放增加。推动可持续森林管理和植树造林是应对措施。",
                "环境污染包括空气污染、水污染和土壤污染等，严重影响人类健康和生态系统。制定严格的环保法规是控制污染的必要手段。",
                "循环经济是一种减少废物产生和资源消耗的经济模式，强调产品、材料和资源的循环利用。这种模式有助于减轻对环境的压力。"
            ],
            "健康": [
                "健康饮食是维持身体健康的基础，包括多摄入蔬菜水果、全谷物和优质蛋白质，减少加工食品和糖的摄入。平衡的饮食有助于预防慢性疾病。",
                "规律运动对身心健康有诸多益处，如增强心肺功能、提高免疫力和改善心理健康。世界卫生组织建议成人每周至少进行150分钟中等强度的有氧运动。",
                "睡眠质量对健康至关重要，充足的睡眠有助于身体恢复、增强免疫力和提高认知功能。成人一般需要每晚7-9小时的睡眠。",
                "心理健康与身体健康同等重要，包括情绪管理、压力应对和积极的心态。保持社交联系、寻求专业帮助和培养爱好都有助于维护心理健康。",
                "预防医学强调通过健康生活方式、定期体检和疫苗接种等预防疾病的发生。预防比治疗更经济有效。",
                "慢性病如心脏病、糖尿病和肥胖症已成为全球健康挑战，良好的生活习惯和早期干预是预防和管理这些疾病的关键。",
                "抗生素耐药性是当今医学面临的严峻挑战，由抗生素过度使用和滥用导致。合理使用抗生素对保护这些宝贵药物的有效性至关重要。",
                "全球卫生合作在应对流行病和提高医疗服务可及性方面发挥着关键作用。加强国际协作有助于应对跨境健康威胁和改善全球健康状况。"
            ],
            "经济": [
                "全球化是指世界经济日益相互依存和一体化的过程，表现为国际贸易、投资和人员流动的增加。全球化带来了经济增长，但也加剧了不平等。",
                "数字经济是基于数字技术和数据的经济活动，包括电子商务、在线服务和数字平台。数字经济正在重塑传统行业和创造新的商业模式。",
                "可持续发展经济强调在满足当代人需求的同时不损害后代满足其需求的能力。它寻求经济增长、社会包容和环境保护之间的平衡。",
                "共享经济是一种基于共享和协作消费的经济模式，如Uber和Airbnb等平台。共享经济提高了资源利用效率，但也带来了监管挑战。",
                "人工智能和自动化正在改变就业市场，一些工作岗位消失，同时创造新的就业机会。适应这一变化需要持续学习和技能更新。",
                "财富不平等是当今社会面临的重要经济和社会问题，表现为收入和财富分配的不均衡。减少不平等需要综合政策，如累进税制和社会保障。",
                "绿色金融是指为支持环境可持续发展而设计的金融服务和产品，如绿色债券和可持续投资。绿色金融在促进低碳经济转型中发挥着重要作用。",
                "创新和创业是经济增长和就业创造的重要驱动力。培养创新文化和支持创业生态系统对于经济发展至关重要。"
            ],
            "教育": [
                "个性化学习是一种教育方法，根据学生的需求、能力和兴趣定制教学内容和方法。技术工具可以支持个性化学习，提高教育效果。",
                "终身学习概念认为学习是一个持续的过程，不限于正规教育阶段。在知识快速更新的时代，终身学习成为适应变化的必要能力。",
                "STEM教育强调科学、技术、工程和数学学科的整合，培养学生的批判性思维和问题解决能力。STEM教育对培养未来人才至关重要。",
                "远程教育利用互联网和数字技术，打破时间和空间限制提供教育服务。COVID-19大流行加速了远程教育的发展和普及。",
                "教育公平关注所有人获得优质教育的机会平等，不受社会经济背景、性别或地理位置的影响。减少教育差距是实现社会公正的关键。"
            ],
            "文化": [
                "文化多样性是指人类社会中存在的各种文化表达形式、传统和价值观的多样性。尊重和保护文化多样性是促进文化间理解和和平的基础。",
                "数字文化是指在数字环境中产生和传播的文化形式，如社交媒体、网络社区和数字艺术。数字文化正在改变人们的交流、创作和消费方式。",
                "传统文化遗产包括物质和非物质文化遗产，如历史建筑、传统工艺和民间习俗。保护文化遗产对于传承历史记忆和文化认同至关重要。",
                "流行文化是指在特定时期内广泛流行的文化表现形式，如音乐、电影和时尚。流行文化反映了社会变化和价值观念的转变。",
                "文化创意产业是指以创意、创新和知识产权为核心的产业，如电影、音乐、出版和设计等。文化创意产业是经济增长的重要驱动力。",
                "跨文化交流指不同文化背景的人之间的互动和交流，促进相互理解和学习。全球化时代，跨文化交流变得日益重要。"
            ],
            "复杂长文本": [
                """
                智能城市是利用各种信息技术或创新概念，将城市的系统和服务连接起来，以提高资源利用效率，优化城市管理和服务，以及改善市民生活质量的城市发展模式。人工智能在智能城市中扮演着重要角色，例如智能交通系统可以利用AI分析交通流量，优化信号灯控制，减少拥堵；智能电网系统可以预测用电需求，平衡供需关系，提高能源利用效率；城市安全监控系统可以利用计算机视觉技术进行异常行为检测和预警。
                与此同时，随着气候变化的加剧，智能城市规划也需要考虑可持续发展因素，包括绿色建筑、可再生能源利用、以及应对极端天气的韧性设计等。数据隐私和安全问题也是智能城市面临的重要挑战，如何平衡技术创新与公民隐私保护，成为城市管理者需要慎重考虑的问题。
                未来城市的发展将更加注重人与自然的和谐共处，技术与人文的平衡融合。智能城市不仅是技术的集成，更是以人为本的可持续发展理念的体现。
                """,
                """
                全球气候变化是21世纪人类面临的最严峻挑战之一，其影响范围广泛而深远。温室气体排放增加导致全球平均气温上升，引发冰川融化、海平面上升、极端天气事件增多等一系列环境问题。气候变化不仅威胁生态系统和生物多样性，还对人类社会的粮食安全、水资源供应、公共卫生和经济发展构成重大挑战。
                应对气候变化需要全球协作和多层次的行动。在国际层面，《巴黎协定》为全球气候治理提供了框架，各国承诺减少温室气体排放，限制全球温升。在国家层面，发展可再生能源、提高能源效率、实施碳定价机制等政策工具被广泛采用。在城市和社区层面，绿色建筑、可持续交通和低碳生活方式正在推广。个人通过改变消费习惯和生活方式也能为减缓气候变化做出贡献。
                气候变化的挑战与机遇并存。向低碳经济转型不仅有助于保护环境，还能创造绿色就业机会和促进技术创新。气候智慧型农业、清洁能源技术和循环经济模式正在开辟可持续发展的新路径。面对气候变化，人类需要团结协作，采取紧急而持续的行动，为当代和后代创造一个更可持续的未来。
                """,
                """
                人工智能(AI)技术的快速发展正在深刻改变人类社会的各个方面。从自动驾驶汽车到智能个人助理，从医疗诊断到金融风险评估，AI应用的范围不断扩大。深度学习、强化学习和自然语言处理等技术的突破使AI系统能够执行越来越复杂的任务，有时甚至超越人类表现。
                然而，AI技术的广泛应用也带来了一系列社会、伦理和政策挑战。就业市场结构正在因自动化而改变，某些工作岗位可能消失，同时创造新型工作。算法偏见和公平性问题引发了人们对AI系统决策过程的担忧。数据隐私保护和安全问题需要得到充分重视。AI技术在军事和监控领域的应用引发了关于适当使用限制的辩论。
                面对这些挑战，负责任的AI发展和治理变得尤为重要。这包括制定伦理准则和监管框架，确保AI技术的发展方向与人类价值观一致；投资教育和培训，使人们能够适应AI驱动的经济；促进国际合作，应对AI带来的全球挑战。人工智能的未来将取决于我们今天做出的选择，如何平衡技术创新与伦理考量，将决定AI是否能真正造福人类社会。
                """
            ]
        }
        
        if category not in samples:
            self.log(f"错误：未找到类别 '{category}'")
            return []
            
        selected_samples = samples[category]
        if num_samples is not None:
            selected_samples = random.sample(selected_samples, min(num_samples, len(selected_samples)))
            
        return selected_samples
        
    def get_query_samples(self):
        """获取测试查询样本
        
        Returns:
            dict: 分类的查询样本
        """
        return {
            "基本查询": [
                "北京有什么著名景点",
                "什么是人工智能",
                "如何应对气候变化",
                "健康饮食的原则是什么",
                "中国的主要城市有哪些"
            ],
            "复合查询": [
                "人工智能在城市管理中的应用",
                "气候变化对城市规划的影响",
                "数字技术如何改变教育方式",
                "可持续发展与经济增长的关系",
                "健康生活方式在现代城市的实践"
            ],
            "稀有词查询": [
                "量子计算技术的发展",
                "区块链在金融领域的应用",
                "生物多样性保护措施",
                "抗生素耐药性问题",
                "虚拟现实与增强现实技术"
            ],
            "长文本相关查询": [
                "智能城市的关键技术",
                "气候变化的全球影响",
                "人工智能的伦理问题",
                "智能城市与可持续发展",
                "AI技术在城市管理中的应用"
            ]
        }
        
    def add_memories_by_category(self):
        """按类别添加记忆"""
        categories = ["科技", "城市", "环境", "健康", "经济", "教育", "文化"]
        total_added = 0
        
        self.log("\n===== 按类别添加记忆 =====")
        
        for category in categories:
            samples = self.load_memory_samples(category)
            self.log(f"\n添加 {category} 类别记忆 ({len(samples)} 条):")
            
            category_added = 0
            for sample in samples:
                result = self.memory.maintain_memory(sample)
                category_added += result["built"]
                
            self.log(f"- {category} 类别添加了 {category_added} 个新记忆")
            total_added += category_added
            
        # 添加复杂长文本
        long_texts = self.load_memory_samples("复杂长文本")
        self.log(f"\n添加复杂长文本 ({len(long_texts)} 条):")
        
        long_text_added = 0
        for text in long_texts:
            result = self.memory.maintain_memory(text)
            long_text_added += result["built"]
            
        self.log(f"- 复杂长文本添加了 {long_text_added} 个新记忆")
        total_added += long_text_added
        
        self.log(f"\n总计添加了 {total_added} 个新记忆")
        
        # 记忆图状态
        node_count = len(self.memory.memory_graph.nodes())
        edge_count = len(self.memory.memory_graph.edges())
        self.log(f"当前记忆图状态: {node_count} 个概念, {edge_count} 个连接")
        
        return total_added
        
    def test_basic_queries(self):
        """测试基本查询功能"""
        self.log("\n===== 基本查询测试 =====")
        
        queries = self.get_query_samples()["基本查询"]
        for query in queries:
            self.log(f"\n查询: '{query}'")
            result = self.memory.get_memories_as_string(query)
            self.log(f"结果:\n{result}")
            
    def test_compound_queries(self):
        """测试复合查询功能"""
        self.log("\n===== 复合查询测试 =====")
        
        queries = self.get_query_samples()["复合查询"]
        for query in queries:
            self.log(f"\n查询: '{query}'")
            result = self.memory.get_memories_as_string(query)
            self.log(f"结果:\n{result}")
            
    def test_rare_word_queries(self):
        """测试稀有词查询功能"""
        self.log("\n===== 稀有词查询测试 =====")
        
        queries = self.get_query_samples()["稀有词查询"]
        for query in queries:
            self.log(f"\n查询: '{query}'")
            result = self.memory.get_memories_as_string(query)
            self.log(f"结果:\n{result}")
            
    def test_long_text_queries(self):
        """测试长文本相关查询功能"""
        self.log("\n===== 长文本相关查询测试 =====")
        
        queries = self.get_query_samples()["长文本相关查询"]
        for query in queries:
            self.log(f"\n查询: '{query}'")
            result = self.memory.get_memories_as_string(query)
            self.log(f"结果:\n{result}")
            
    def analyze_memory_graph(self):
        """分析记忆图结构"""
        self.log("\n===== 记忆图分析 =====")
        
        # 基本统计
        node_count = len(self.memory.memory_graph.nodes())
        edge_count = len(self.memory.memory_graph.edges())
        self.log(f"记忆图状态: {node_count} 个概念, {edge_count} 个连接")
        
        # 计算平均连接度
        if node_count > 0:
            avg_degree = 2 * edge_count / node_count
            self.log(f"平均连接度: {avg_degree:.2f}")
            
        # 查找连接最多的概念
        if node_count > 0:
            concept_degrees = [(node, len(list(self.memory.memory_graph.neighbors(node)))) 
                              for node in self.memory.memory_graph.nodes()]
            concept_degrees.sort(key=lambda x: x[1], reverse=True)
            
            self.log("\n连接最多的概念 (Top 10):")
            for concept, degree in concept_degrees[:10]:
                self.log(f"- '{concept}': {degree} 个连接")
                
        # 记忆项最多的概念
        if node_count > 0:
            concept_memories = []
            for node in self.memory.memory_graph.nodes():
                memory_items = self.memory.memory_graph.nodes[node].get("memory_items", [])
                if not isinstance(memory_items, list):
                    memory_items = [memory_items]
                concept_memories.append((node, len(memory_items)))
                
            concept_memories.sort(key=lambda x: x[1], reverse=True)
            
            self.log("\n记忆项最多的概念 (Top 10):")
            for concept, count in concept_memories[:10]:
                self.log(f"- '{concept}': {count} 条记忆")
                
        # 显示主要概念的连接
        main_concepts = ["人工智能", "城市", "气候变化", "健康", "技术"]
        for concept in main_concepts:
            if concept in self.memory.memory_graph:
                neighbors = list(self.memory.memory_graph.neighbors(concept))
                self.log(f"\n概念 '{concept}' 的连接 ({len(neighbors)}):")
                for neighbor in sorted(neighbors)[:5]:  # 只显示前5个连接
                    if concept in self.memory.memory_graph and neighbor in self.memory.memory_graph[concept]:
                        strength = self.memory.memory_graph[concept][neighbor].get("strength", 1)
                        self.log(f"- '{neighbor}' (强度: {strength})")
                        
    def run_comprehensive_test(self):
        """运行全面测试"""
        self.log("===== 大规模记忆系统测试开始 =====")
        self.log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 添加大量记忆
        self.add_memories_by_category()
        
        # 2. 基本查询测试
        self.test_basic_queries()
        
        # 3. 复合查询测试
        self.test_compound_queries()
        
        # 4. 稀有词查询测试
        self.test_rare_word_queries()
        
        # 5. 长文本相关查询测试
        self.test_long_text_queries()
        
        # 6. 记忆图分析
        self.analyze_memory_graph()
        
        # 保存测试结果
        self.log(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("===== 大规模记忆系统测试结束 =====")
        self.save_results()

def main():
    # 创建评估器并运行全面测试
    evaluator = MemorySystemEvaluator(clean_start=True)
    evaluator.run_comprehensive_test()

if __name__ == "__main__":
    main() 