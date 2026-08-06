# Qbot1.5 — AI 聊天机器人完整使用教程

## 项目简介

Qbot1.5 是一个基于大语言模型的 AI 聊天机器人，由**幻日**编写。
它通过 LLOneBot 桥接 QQ，支持群聊/私聊自动回复、AI 语音合成、AI 绘画、
海龟汤（情境推理游戏）等丰富功能，并具备记忆系统与多模型支持。

- **开源协议**：MIT
- **联系方式**：QQ 2141073363
- **适用平台**：Windows（内置 Python 运行时）

> **极简使用**：本项目设计为开箱即用。你只需要在 `set.json` 中修改人设提示词，然后双击 `双击启动Qbot1.5.bat` 就可以让 AI 在 QQ 上陪你聊天了。不需要安装 Python，不需要配置复杂环境，项目自带运行时。

### 极简三步走

1. **改人设**：编辑 `set.json`，修改 `system_prompts` 中的角色设定为你想要的 AI 人设；项目已内置基础AI模型，可以直接使用
2. **启动**：双击 `双击启动Qbot1.5.bat`
3. **聊天**：在 QQ 群或私聊中 @机器人 或发送触发词，AI 自动回复

> 更多高级功能（语音、绘画、翻唱、海龟汤）需额外配置，但基础聊天开箱即用。

---

## 目录

1. [环境准备](#1-环境准备)
2. [项目结构](#2-项目结构)
3. [快速启动](#3-快速启动)
4. [配置说明](#4-配置说明)
5. [功能模块](#5-功能模块)
6. [自定义角色](#6-自定义角色)
7. [常见问题](#7-常见问题)
8. [开发者指南](#8-开发者指南)

---

## 1. 环境准备

### 1.1 Python 环境

项目自带 `py/` 目录（含 `python.exe` 及依赖包），**无需额外安装 Python**。
如需自行安装，请使用 **Python 3.10+**。

### 1.2 LLOneBot（QQ 桥接）

Qbot 依赖 LLOneBot 对接 QQ 消息。

1. 打开 `tools/llonebot/llbot.exe`
2. 按提示登录你的 QQ 机器人账号
3. LLOneBot 会自动在 `tools/llonebot/bin/llbot/data/` 生成配置文件
4. Qbot 启动时会自动写入 LLOneBot 的对接配置

### 1.3 大模型 API

Qbot 支持多种 LLM 后端，需在 `set.json` 中配置：

| 功能 | 支持的模型/API | 配置字段 |
|------|----------------|-----------|
| 聊天 | GLM-4-Flash / Qwen / 其他 OpenAI 兼容 API | `chat_models` |
| 搜索 | GLM-4-Flash（网络搜索工具） | `glm_search()` |
| 绘画 | CogView / StabilityAI / ModelScope / SiliconFlow | `draw_url`, `draw_key`, `draw_model` |
| 多模态视觉 | GLM-4V-Flash | `see_url`, `see_key`, `see_model` |

> **注意**：请在 `set.json` 中填入你自己的 API Key。

---

## 2. 项目结构

```
qbot1.5/
├── Qbot.py                  # 主程序入口
├── set.json                   # 核心配置文件
├── soups.json                 # 海龟汤（情境推理）题库
├── 双击启动Qbot1.5.bat       # 一键启动脚本
├── py/                          # 内置 Python 运行时
├── module/                        # 核心模块
│   ├── sfunc.py             # 消息过滤、记忆摘要工具
│   ├── receive.py             # 消息接收（Socket 监听）
│   ├── soup_ai.py           # 海龟汤游戏模块
│   ├── key_memory.py        # 关键词记忆系统
│   ├── memory_interface.py   # 记忆接口
│   ├── memory_system.py      # 记忆系统核心
│   ├── indextts.py         # IndexTTS 语音合成
│   ├── mem_i.py           # 记忆接口 v2
│   └── write_llbot_config.py  # LLOneBot 配置写入
├── data/                          # 数据目录
│   ├── llbot_config/             # LLOneBot 配置
│   ├── msface/                   # QQ 表情包目录
│   └── voice/                    # 语音模型目录
├── memory/                        # 记忆存储
│   ├── AI幻蓝/
│   │   ├── auto_memory.json     # 自动记忆
│   │   └── user_memory.json     # 用户记忆
│   └── mem_i/
│       └── memory.json          # 索引记忆
├── user/                          # 用户/群聊记忆数据
│   ├── furina/                    # 角色专属目录
│   ├── g<群号>/                   # 群聊记忆
│   │   ├── memory.txt
│   │   └── memory.json
│   └── ...
├── tools/                         # 工具目录
│   └── llonebot/                  # LLOneBot QQ 桥接工具
│       ├── llbot.exe
│       └── 使用说明.txt
└── module/simple_memory/             # 简易记忆系统（含独立 README）
```

---

## 3. 快速启动

### 3.1 一键启动

双击 **`双击启动Qbot1.5.bat`** 即可运行。

### 3.2 手动启动

```bash
.\py\python.exe Qbot.py
```

### 3.3 启动流程

1. Qbot 读取 `set.json` 中的配置（角色、端口、模型等）
2. 自动写入 LLOneBot 的对接配置
3. 启动 Socket 监听，等待 LLOneBot 推送消息
4. 收到消息后，触发 AI 回复流程：
   - 关键词记忆匹配 → 调用 LLM 生成回复 → 发送回复消息
   - 可选：语音合成、AI 绘画、海龟汤游戏等

---

## 4. 配置说明

### 4.1 `set.json` 核心配置

```json
{
  "role": {
    "furina": {
      "AI_name": "芙宁娜",
      "qq_id": "1963196536",
      "triggers": ["芙芙", "芙宁娜"],
      "system_prompts": {
        "default": "...",
        "unhappy": "...",
        "happy": "...",
        "angry": "...",
        "gentle": "..."
      },
      "send_port": 3050,
      "listen_port": 3051,
      "debug": false,
      "random_trigger": 30,
      "max_turn_group": 14,
      "max_turn_private": 10,
      "root_ids": [2141073363, 1610410288],
      "song": true,
      "singer": "furina",
      "is_voice": true,
      "speaker": "fufuvoice",
      "send_debug": false,
      "is_ban_set": true,
      "think": false
    }
  },
  "ban_names": ["幻蓝", "芙芙", "AI", ...],
  "think_keywords": [["```thinking", "```"], ["<think>", "</think>"]],
  "tts_version": 2,
  "tts_url": "<你的TTS服务地址>",
  "draw_url": "...",
  "draw_key": "在这里配置密钥",
  "draw_model": "...",
  "see_url": "...",
  "see_key": "...",
  "see_model": "...",
  "chat_models": [
    {
      "model_api": "...",
      "model_key": "...",
      "model_name": "...",
      "weight": 10
    }
  ]
}
```

### 4.2 配置项详解

| 配置项 | 说明 |
|---------|------|
| `role` | 角色定义，支持多角色（如 `furina`） |
| `AI_name` | AI 在对话中使用的名字 |
| `qq_id` | 机器人登录的 QQ 号 |
| `triggers` | 触发词，消息包含这些词时 AI 会回复 |
| `system_prompts` | 不同情感状态的系统提示词（default/unhappy/happy/angry/gentle） |
| `send_port` | 发送消息的端口（对接 LLOneBot） |
| `listen_port` | 监听 QQ 消息的 Socket 端口 |
| `debug` | 是否开启调试模式 |
| `random_trigger` | 无触发词时自动回复的概率分母（1/n） |
| `max_turn_group` | 群聊历史对话轮数上限 |
| `max_turn_private` | 私聊历史对话轮数上限 |
| `root_ids` | 管理员 QQ 号列表 |
| `song` | 是否启用 AI 翻唱 |
| `singer` | 翻唱歌手的模型名称 |
| `is_voice` | 是否启用语音合成 |
| `speaker` | 语音合成的说话人名称 |
| `send_debug` | 是否发送调试信息到 QQ |
| `is_ban_set` | 是否启用禁言功能 |
| `think` | 是否启用思考模型 |
| `ban_names` | 屏蔽的用户名/关键词（防止 AI 互刷） |
| `think_keywords` | 思考模型的标记关键词对 |
| `tts_version` | 语音合成版本（1=GPTSoVITS, 2=IndexTTS v2） |
| `tts_url` | 语音合成服务地址 |
| `chat_models` | 聊天模型列表（支持多模型加权轮询） |

### 4.3 `soups.json` — 海龟汤题库

```json
{
  "soups": [
    {
      "id": "soup-004",
      "标题": "墓碑上的名字",
      "汤面": "...",
      "汤底": "...",
      "任务目标": "...",
      "提问次数": 20,
      "允许提示": true,
      "提示列表": ["提示1", "提示2"]
    }
  ]
}
```

---

## 5. 功能模块

### 5.1 智能聊天

- 支持群聊和私聊自动回复
- 自动根据上下文和情感状态切换系统提示词
- 多模型加权选择（`chat_models` 权重配置）
- 短期记忆：最近 N 轮对话上下文
- 长期记忆：关键词匹配 + 文件记忆检索

### 5.2 记忆系统

Qbot 具备三层记忆架构：

1. **关键词记忆（KeyMemory）**：`auto_memory.json` / `user_memory.json`
   - 自动提取并存储对话中的关键信息
   - 命中时增加权重，未命中时递减
2. **文件记忆（get_memory）**：从 `user/<角色>/memory.txt` 中按关键词检索相关文段
3. **简易记忆（SimpleMemory）**：基于图的语义记忆系统，支持增删查遗

### 5.3 AI 语音合成（TTS）

- 支持 GPT-SoVITS（v1）和 IndexTTS v2
- 配置 `tts_url` 指向本地语音服务
- 在对话中 AI 自动判断何时输出语音

### 5.4 AI 绘画

- 支持 CogView / StabilityAI / ModelScope / SiliconFlow
- 群聊/私聊均可触发
- 图片保存到 `data/image/<角色>/` 并通过 QQ 发送

### 5.5 AI 翻唱

- 对接本地翻唱服务（需提前配置好模型）
- 启用 `song: true` 后，AI 在合适时机自动唱歌

### 5.6 海龟汤（情境推理游戏）

- 基于 `soups.json` 题库
- AI 作为主持人，玩家通过是/否提问推理真相
- 支持提示、提问次数限制、最终猜测验证
- 需要在module/soup_ai.py文件开头独立配置AI模型

### 5.7 网络搜索

- 三级搜索策略：openinterpreter API → GLM-4-Flash → Bing 搜索
- 自动提取搜索结果摘要和详细内容

### 5.8 群管理

- **禁言**：`is_ban_set: true` 时 AI 可对骚扰用户执行禁言
- **Ban 名单**：`ban_names` 屏蔽指定用户或 AI 互刷
- **管理员**：`root_ids` 中的 QQ 号拥有管理权限

---

## 6. 自定义角色

### 6.1 添加新角色

在 `set.json` 的 `role` 对象中添加新角色配置：

```json
"role": {
  "furina": { ... },
  "your_new_role": {
    "AI_name": "你的AI名字",
    "qq_id": "你的机器人QQ号",
    "triggers": ["触发词1", "触发词2"],
    "system_prompts": {
      "default": "你的人设提示词..."
    },
    "send_port": 3050,
    "listen_port": 3051,
    "random_trigger": 30,
    "max_turn_group": 14,
    "max_turn_private": 10,
    "root_ids": [管理员QQ号],
    "song": false,
    "is_voice": false,
    "think": false
  }
}
```

### 6.2 人设提示词编写建议

```
[Character setting]
你是<角色名>，描述性格、背景、说话风格...

[example]
场景1回复
场景2回复

[impression]
对特定人的印象和态度

[mood]default / happy / unhappy / angry / gentle
```

### 6.3 创建用户数据目录

```bash
# 为每个角色/群创建独立的记忆存储
mkdir user/<角色名>/all/I_memory.txt
mkdir user/g<群号>/
```

---

## 7. 常见问题

### Q1: 启动后没有反应？
- 确认 `tools/llonebot/llbot.exe` 已启动并登录了 QQ
- 检查 `send_port` 和 `listen_port` 是否与 LLOneBot 配置一致
- 确认端口未被占用

### Q2: AI 不回复消息？
- 检查消息是否包含 `triggers` 中的触发词
- 确认 `random_trigger` 概率触发是否命中
- 检查 `chat_models` 中的 API 是否正常

### Q3: 语音/绘画不工作？
- 确认本地 TTS 服务已启动，`tts_url` 地址正确
- 确认绘画 API Key 已配置

### Q4: 记忆系统不生效？
- 确认 `memory/` 目录下的 JSON 文件格式正确
- 确认 `user/` 目录下有对应的角色文件夹

### Q5: 想更换大模型？
- 在 `set.json` 的 `chat_models` 中添加/修改模型配置
- 支持任意 OpenAI 兼容 API 端点的模型

### Q6: 如何添加海龟汤题目？
- 编辑 `soups.json`，按照现有格式添加新的汤面/汤底

---

## 8. 开发者指南

### 8.1 项目架构

```
LLOneBot → Socket → Qbot.py
                              ├── 消息解析 (request_to_json)
                              ├── 关键词匹配 (KeyMemory)
                              ├── 记忆检索 (get_memory)
                              ├── LLM 调用 (多模型加权)
                              ├── 回复生成
                              └── 消息发送 (send_msg / send_image)
```

### 8.2 二次开发注意事项

- 修改代码后请在文件头部留下你的联系方式
- 遵守 MIT 开源协议
- 不可用于不合法不合规的行为

### 8.3 核心模块说明

| 模块 | 功能 |
|------|------|
| `Qbot.py` | 主程序：消息收发、搜索、绘画、TTS 调度 |
| `sfunc.py` | 消息过滤、系统提示词增强、对话摘要 |
| `receive.py` | Socket 消息接收 |
| `soup_ai.py` | 海龟汤主持人逻辑 |
| `key_memory.py` | 关键词记忆（自动/用户记忆） |
| `indextts.py` | IndexTTS 语音合成请求 |
| `write_llbot_config.py` | 自动生成 LLOneBot 配置 |
| `memory_system.py` | 图结构语义记忆 |

### 8.4 添加自定义功能

```python
# 在 Qbot.py 中添加新功能
def my_custom_feature(query):
    # 你的逻辑
    return result

# 在消息处理循环中调用
```

---

## 联系方式

- **作者**：幻日
- **QQ**：2141073363
- **开源地址**：MIT 协议

> 本项目仅供交流学习，不可进行不合法不合规的行为。
