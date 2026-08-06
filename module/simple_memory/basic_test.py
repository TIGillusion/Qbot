print("Hello World")
print("This is a basic test")
print("Testing output functionality")

# 测试依赖导入
try:
    import networkx as nx
    print(f"NetworkX version: {nx.__version__}")
except ImportError:
    print("NetworkX not installed")

try:
    import jieba
    print(f"Jieba loaded successfully")
except ImportError:
    print("Jieba not installed")

try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError:
    print("NumPy not installed") 