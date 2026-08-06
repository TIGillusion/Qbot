import random
import re
import json
import requests

def filted(input_string, words_to_replace):
    replacements = ['喵', '汪', '嘤']
    outputstring = input_string

    for word in words_to_replace:
        # 查找所有匹配的词
        for match in re.finditer(re.escape(word), outputstring):
            # 选择一个随机的替换字
            replacement_char = random.choice(replacements)
            # 生成与原词等长的替换字符串
            replacement_word = replacement_char * len(word)
            # 替换匹配的词
            outputstring = outputstring[:match.start()] + replacement_word + outputstring[match.end():]

    return outputstring

def make_enhance_system_prompt(system_prompt,AI_name):
    return f"""
你是一个高情商的聊天大师，接下来你需要根据下述人设以及后续输入的对话上文来思考当前应该如何回复，需要详细描述思考分析的过程（尽可能详细周到的分析所有已知信息和上下文，指出和{AI_name}相关的需要回复的部分）
以下是人设:
<role_prompt>
{system_prompt}
</role_prompt>
另外也可以关注上述包含的指令，思考是否需要使用以及具体使用什么指令名称（注意指令格式，符号和名称）
[回复需尽可能简洁但面面俱到，不超过100字]"""

def enhance_response(system_prompt,history,input,AI_name,url,model,key):
    chat_history="<对话上文>\n"
    for per_chat in history:
        if per_chat["role"]=="user":
            chat_history+=per_chat["content"]
        if per_chat["role"] == "assistant":
            chat_history+=f"\n{AI_name}:{per_chat['content']}\n"
    chat_history+=f"\n</对话上文>\n<当前消息>\n{input}\n</当前消息>\n"
    ask = "请你观察分析并根据以下信息以及人设信息确定当前对话状况\n"+chat_history+f"假设你是{AI_name}，根据上文和前面的要求有条理的分析你的回复应该是哪方面？是否需要具体使用哪些指令执行什么操作？（注意主次和逻辑以及简述上文对话话题，当前场景和当前消息相关的上文。只需给出分析，注意只给出分析和思考而不是让你代入角色进行回复。回复字数尽可能少）"
    messages=[{
        "role":"system",
        "content":system_prompt
    },
    {
        "role":"user",
        "content":ask
    }]
    data={
            "model": model,
            "messages":messages,
            "stream": True
        }
    headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer "+key
        }
    response=requests.post(url=url,headers=headers,stream=True,data=json.dumps(data))
    answer=""
    for line in response.iter_lines():
        try:
            decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
            if decoded != '':
                answer+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
        except Exception as e:
            pass
    if answer.strip():
        return f"\n<think>\n{answer}\n</think>"
    else:
        return ""

def summarize_chat(history,AI_name,url,model,key):
    system_prompt = """你的任务是根据聊天记录分析当前聊天的话题，场景，气氛并总结聊天中提到的信息，概况聊天内容"""
    chat_history="<对话上文>\n"
    for per_chat in history:
        if per_chat["role"]=="user":
            chat_history+=per_chat["content"]
        if per_chat["role"] == "assistant":
            chat_history+=f"\n{AI_name}:{per_chat['content']}\n"
    ask = "请你观察分析并总结以下聊天对话内容"+chat_history+f"简述当前聊天的话题，过程，与{AI_name}相关的关键信息"
    messages=[{
        "role":"system",
        "content":system_prompt
    },
    {
        "role":"user",
        "content":ask
    }]
    data={
            "model": model,
            "messages":messages,
            "stream": True
        }
    headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer "+key
        }
    response=requests.post(url=url,headers=headers,stream=True,data=json.dumps(data))
    answer=""
    for line in response.iter_lines():
        try:
            decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
            if decoded != '':
                answer+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
        except Exception as e:
            pass
    return f"\n<recap>\n{answer}\n</recap>"

def strip_chars(s, chars_to_strip):
    """
    去掉字符串开头和结尾的连续指定字符
    
    参数:
        s (str): 原始字符串
        chars_to_strip (str): 需要去除的字符集合
    
    返回:
        str: 处理后的字符串
    """
    if not s or not chars_to_strip:
        return s
    
    # 去掉开头的字符
    start = 0
    while start < len(s) and s[start] in chars_to_strip:
        start += 1
    
    # 去掉结尾的字符
    end = len(s)
    while end > start and s[end - 1] in chars_to_strip:
        end -= 1
    
    return s[start:end]

if __name__=="__main__":
    # 示例输入
    input_string = "苹果香蕉 橙子 苹果 梨"
    words_to_replace = ["苹果", "香蕉", "橙子"]
    # 调用函数并打印结果
    result=filted(input_string, words_to_replace)
    print(result)
