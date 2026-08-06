import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)

print('\n欢迎使用由幻日编写的Qbot-1程序，有疑问请联系第一开发者幻日q：2141073363，项目维护者高远q：1967444797')
import sys
sys.path.append(".")
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import time
from datetime import datetime
import random
import requests
import json
import os
from module.sfunc import *
import socket
import re
from threading import Thread
import base64
from PIL import Image
from io import BytesIO
import jieba.analyse
from bs4 import BeautifulSoup
from zhipuai import ZhipuAI
from datetime import datetime
from module.mem_i import MEM_I
from module.indextts import IndexTTS2RequestData

from module.soup_ai import TurtleSoupHost

from module.write_llbot_config import write_llbot_config


 

 
def request_to_json(msg):
    dicstrmsg=msg.split("\r\n\r\n")[-1]
    return json.loads(dicstrmsg)
    for i in range(len(dicstrmsg)):
        if msg[i]=="{" and msg[-1]=="\n":
            return json.loads(msg[i:])
    return None
 
# 需要循环执行，返回值为json格式
def rev_msg():# json or None
    HttpResponseHeader = '''HTTP/1.1 200 OK
Content-Type: text/html
'''
    Client, Address = ListenSocket.accept()
    Request = Client.recv(10240).decode(encoding='utf-8')
    rev_json=request_to_json(Request)
    Client.sendall((HttpResponseHeader).encode(encoding='utf-8'))
    Client.close()
    return rev_json

def change_setting(file_name,key,value):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            t_gsetting=json.load(f)
    
        t_gsetting[key]=value
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(t_gsetting, f, ensure_ascii=False, indent=4)
    except Exception as e:
        with open("./data/idname.json","w",encoding="utf-8") as tpass:
            tpass.write('{"0":"未知"}')
        print(e)



def run_v4_sync(query):
    msg = [
        {
            "role": "user",
            "content":query
        }
    ]
    tool = "web-search-pro"
    url = "https://open.bigmodel.cn/api/paas/v4/tools"
    data = {
        "tool": tool,
        "stream": False,
        "messages": msg
    }

    resp = requests.post(
        url,
        json=data,
        headers={'Authorization': "31598f74ee9776d64b85b0a0457d9094.EKpxafHYqcpiElrE"},
        timeout=300
    )
    decoded=resp.content.decode()
    result_json=json.loads(decoded)
    result_list=result_json["choices"][0]["message"]["tool_calls"][1]["search_result"]
    result='\n'
    for p_result in result_list:
        result+=("---"+p_result["title"]+"\nlink:"+p_result["link"]+'\ncontent:'+p_result["content"]+"\n\n")
        if len(result)>600:
            break
    print(result)
    return result

def glm_search(query):
    

    # 初始化 ZhipuAI 客户端
    client = ZhipuAI(api_key="31598f74ee9776d64b85b0a0457d9094.EKpxafHYqcpiElrE")

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 设置工具（启用网络搜索）
    tools = [{
        "type": "web_search",
        "web_search": {
            "enable": True  # 启用网络搜索
        }
    }]

    # 系统提示模板，包含时间信息
    system_prompt = f"""你是一个具备网络访问能力的智能助手，在适当情况下，优先使用网络信息（参考信息）来回答，
    以确保用户得到最新、准确的帮助。当前日期是 {current_date}。"""

    # 用户输入的问题
    user_input = query

    # 构建动态用户问题提示
    user_question = f"参考最新消息给出对用户输入的搜索关键词的结果的详细的回答: {user_input}"

    # 构建消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    # 生成响应
    response = client.chat.completions.create(
        model="glm-4-Flash",
        messages=messages,
        tools=tools
    )

    # 输出结果
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def search(query):
    """
    Searches the web for the specified query and returns the results.
    """
    response = requests.get(
        'https://api.openinterpreter.com/v0/browser/search',
        params={"query": query},
    )
    try:
        if response.status_code==200 and response.json()["result"]:
            return response.json()["result"]
        else:
            raise ValueError
    except Exception as e:
        result = glm_search(query)
        if result:
            return result

        result = run_v4_sync(query)
        if result:
            return result
        else:
            querys=query.split(" ")
            result = bing_search(querys)
            if result:
                return result
            else:
                return "未搜索到合适结果"

def bing_search(keywords):
    q=""
    for p_k in keywords:
        q+=(p_k+"+")
    # 必应搜索结果URL
    url = 'https://cn.bing.com/search?q=%s&count=10&qs=n&sp=-1&lq=0&pq=%s'%(q[:-1],q[:-1])
    # 请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, headers=headers)
        # 确保请求成功
        response.raise_for_status()
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找搜索结果
        search_items = soup.find_all('li', class_='b_algo')
        
        if not search_items:
            print("未找到搜索结果，可能是因为HTML结构发生了变化。")
            return ""
        result = ""
        for index, item in enumerate(search_items):
            # 提取标题
            title = item.find('h2').get_text()
            # 提取链接
            link = item.find('a')['href']
            # 提取摘要
            summary_div = item.find('div', class_='b_caption')
            if summary_div:
                summary_p = summary_div.find_all('p')
                if summary_p:
                    summary = ''.join(p.get_text() for p in summary_p)
                else:
                    summary = summary_div.get_text(strip=True)
            else:
                summary = ''
            
            # 对于前三个结果，获取详细页面内容
            if index < 10:
                try:
                    # 发送GET请求到详细页面
                    response_detail = requests.get(link, headers=headers)
                    response_detail.raise_for_status()
                    soup_detail = BeautifulSoup(response_detail.text, 'html.parser')
                    # 假设详细页面中的主要内容在 <div id="content"> 中
                    content_div = soup_detail.find('div', id='content')
                    if content_div:
                        content = content_div.get_text(strip=True)
                        # 保留前500个字符
                        content = (content[:5000]) if len(content) > 500 else content
                    else:
                        content = '无法找到详细内容。'
                    result+=f'标题：{title}\n链接：{link}\n摘要：{summary}\n详细内容：{content}\n'
                    print(f'标题：{title}\n链接：{link}\n摘要：{summary}\n详细内容：{content}\n')
                except requests.RequestException as e:
                    print(f'请求详细页面错误：{e}')
            else:
                # 打印摘要
                result+=f'标题：{title}\n链接：{link}\n摘要：{summary}\n详细内容：{content}\n'
                print(f'标题：{title}\n链接：{link}\n摘要：{summary}\n')
            if len(result) > 5000:
                return result
        return result

    except requests.RequestException as e:
        print(f'请求错误：{e}')
    except Exception as e:
        print(f'解析错误：{e}')

def merge_contents(data):
    # 初始化一个新的列表来存储处理后的数据
    data=[data[0]]+[{"role":"user","content":" "}]+data[1:]
    new_data = []
    # 用于临时存储连续相同role的内容
    temp_content = ""
    # 上一个role的值
    prev_role = None

    for item in data:
        current_role = item['role']
        current_content = item['content']

        # 如果当前content为空，则将其改为空格
        if not current_content.replace(" ",''):
            if prev_role=="system":
                pass
            elif current_role == "user":
                current_role="assistant"
                current_content = " "
            else:
                current_role="user"
                current_content = " "

        # 如果当前role与上一个role相同，则合并content
        if current_role == prev_role:
            temp_content += current_content
        else:
            # 如果临时内容不为空，则将其作为一个新条目添加到新数据列表中
            if temp_content:
                new_data.append({'role': prev_role, 'content': temp_content})
            # 更新临时内容和上一个role的值
            temp_content = current_content
            prev_role = current_role

    # 添加最后一个临时内容（如果有）
    if temp_content:
        new_data.append({'role': prev_role, 'content': temp_content})

    return new_data

def get_I_memory(file_path):
    with open(f"./user/{role}/all/I_memory.txt","r",encoding="utf-8") as file:
        content1 = file.read()
    existtextlist=content1.split(" ")
    with open(file_path, 'r', encoding='utf-8') as file:
        content2 = file.read()
    for ptext in existtextlist:
        content2=content2.replace(ptext,"")
    
    return "\n[self_impression]\n"+content1[-200:]+"\n"+content2[-200:]

def get_memory(file_path, keywords, match_n=200, time_n=200, radius=50, length=409600):
    """
    读取整个文件，搜索关键词，合并重叠文段，并返回两个排序的文段列表：
    1. 包含关键词个数排名前五的文段。
    2. 越靠近文段末尾的排在前面，同样返回五个，且不与第一个列表重复。

    :param file_path: 文件路径
    :param keywords: 关键词列表
    :param radius: 关键词附近要返回的文本字数
    :return: 关键词匹配记忆
    """
    if not os.path.exists(file_path):
        with open(file_path,"w") as f:
            f.write("")
    # 读取整个文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()[-length:-5000]

    # 构建正则表达式，用于匹配任意一个关键词
    keywords_pattern = '|'.join(map(re.escape, keywords))
    matches = list(re.finditer(keywords_pattern, content))

    # 合并重叠的文段
    merged_blocks = []
    for match in matches:
        start_index = max(match.start() - radius, 0)
        end_index = min(match.end() + radius, len(content))
        # 检查是否与现有文段重叠
        overlap = False
        for block in merged_blocks:
            if start_index < block['end'] and end_index > block['start']:
                # 合并文段
                block['start'] = min(start_index, block['start'])
                block['end'] = max(end_index, block['end'])
                block['count'] += 1
                overlap = True
                break
        if not overlap:
            merged_blocks.append({'start': start_index, 'end': end_index, 'count': 1})

    # 提取文段文本并按关键词个数排序
    text_blocks = [{'text': content[block['start']:block['end']], 'count': block['count']} for block in merged_blocks]
    sorted_by_count = sorted(text_blocks, key=lambda x: x['count'], reverse=True)[:5]

    # 提取文段文本并按文段末尾位置排序
    text_blocks = [{'text': content[block['start']:block['end']], 'end': block['end']} for block in merged_blocks]
    sorted_by_end = sorted(text_blocks, key=lambda x: x['end'], reverse=True)

    # 移除与按关键词个数排序的文段重复的部分
    non_duplicate_sorted_by_end = [block for block in sorted_by_end if block['text'] not in [b['text'] for b in sorted_by_count]][:5]


    main_text = ''
    for per_text in non_duplicate_sorted_by_end:
        main_text+="--%s\n"%per_text["text"]
        if len(main_text) > match_n:
            break
    
    for per_text in sorted_by_count:
        main_text+="--%s\n"%per_text["text"]
        if len(main_text) > match_n+time_n:
            break

    return main_text[:match_n+time_n+200]

def draw_group(prompt,to):
    try:
        urldraw=draw_url
        headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer "+draw_key
            }
        if "cogview" in draw_model or "stabilityai/" in draw_model or "api.siliconflow.cn" in urldraw or "modelscope.cn" in urldraw:
            data={
                "model":draw_model,
                "prompt":prompt,
            }
        else:
            data={
                "model":draw_model,##claude-3-opus-vf
                "messages":[{"role":"user","content":prompt}],
                "stream": True
            }
        send_msg({'msg_type': 'group', 'number': to, 'msg': '正在绘画[%s]中...'%prompt})
        response=requests.post(url=urldraw,headers={**headers, "X-ModelScope-Async-Mode": "true"},stream=True,data=json.dumps(data))
        if response.status_code==200:
            pass
        processed_d_data_draw=''
        for line in response.iter_lines():
            try:
                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                if decoded != '':
                    if "cogview" in draw_model or "stabilityai/" in draw_model or "api.siliconflow.cn" in urldraw:
                        processed_d_data_draw+=json.loads(decoded)["data"][0]["url"]
                        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
                        print(image_url)
                    elif "modelscope.cn" in urldraw:
                        response.raise_for_status()
                        task_id = json.loads(decoded)["task_id"]
                    else:
                        processed_d_data_draw+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
                        print(image_url)
                    print(decoded)
            except Exception as e:
                print(e)
        
        max_n=500
        for n in range(0,max_n):
            try:
                name=str(random.randrange(100000,999999))+'.png'
                if "modelscope.cn" in draw_url:
                    result = requests.get(
                        f"https://api-inference.modelscope.cn/v1/tasks/{task_id}",
                        headers={**headers, "X-ModelScope-Task-Type": "image_generation"},
                    )
                    result.raise_for_status()
                    data = result.json()
                    if data["task_status"] == "SUCCEED":
                        image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
                        image.save(f"./data/image/{role}/%s"%name)
                        
                    elif data["task_status"] == "FAILED":
                        print("Image Generation Failed.")
                        raise ConnectionError("Image Generation Failed.")
                    else:
                        print(n)
                        time.sleep(5)
                        continue
                else:
                    image_response=requests.get(image_url)
                    with open(f"./data/image/{role}/%s"%name,'wb') as f_image:
                        f_image.write(image_response.content)
                send_msg({'msg_type': 'group', 'number': to, 'msg': '绘画完毕发送中...'})
                send_image({'msg_type': 'group', 'number': to, 'msg':name })
                break
            except:
                print(n)
                if n==max_n-1:
                    raise TimeoutError("重试无效")
    except Exception as e:
        print('绘画错误:',e)
        send_msg({'msg_type': 'group', 'number': to, 'msg':'AI绘画操作无法执行'})

def draw_private(prompt,to):
    try:
        urldraw=draw_url
        headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer "+draw_key
            }
        
        if "cogview" in draw_model or "stabilityai/" in draw_model or "api.siliconflow.cn" in urldraw or "modelscope.cn" in urldraw:
            data={
                "model":draw_model,
                "prompt":prompt,
            }
        else:
            data={
                "model":draw_model,##claude-3-opus-vf
                "messages":[{"role":"user","content":prompt}],
                "stream": True
            }
        send_msg({'msg_type': 'private', 'number': to, 'msg': '正在绘画[%s]中...'%prompt})
        response=requests.post(url=urldraw,headers={**headers, "X-ModelScope-Async-Mode": "true"},stream=True,data=json.dumps(data))
        if response.status_code==200:
            pass
        processed_d_data_draw=''
        for line in response.iter_lines():
            try:
                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                if decoded != '':
                    if "cogview" in draw_model or "stabilityai/" in draw_model or "api.siliconflow.cn" in urldraw:
                        processed_d_data_draw+=json.loads(decoded)["data"][0]["url"]
                        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
                        print(image_url)
                    elif "modelscope.cn" in urldraw:
                        response.raise_for_status()
                        task_id = json.loads(decoded)["task_id"]
                    else:
                        processed_d_data_draw+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
                        print(image_url)
                    print(decoded)
            except Exception as e:
                print(e)
        
        max_n=500
        for n in range(0,max_n):
            try:
                name=str(random.randrange(100000,999999))+'.png'
                if "modelscope.cn" in draw_url:
                    result = requests.get(
                        f"https://api-inference.modelscope.cn/v1/tasks/{task_id}",
                        headers={**headers, "X-ModelScope-Task-Type": "image_generation"},
                    )
                    result.raise_for_status()
                    data = result.json()
                    if data["task_status"] == "SUCCEED":
                        image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
                        image.save(f"./data/image/{role}/%s"%name)
                        
                    elif data["task_status"] == "FAILED":
                        print("Image Generation Failed.")
                        raise ConnectionError("Image Generation Failed.")
                    else:
                        print(n)
                        time.sleep(5)
                        continue
                else:
                    image_response=requests.get(image_url)
                    with open(f"./data/image/{role}/%s"%name,'wb') as f_image:
                        f_image.write(image_response.content)
                send_msg({'msg_type': 'private', 'number': to, 'msg': '绘画完毕发送中...'})
                send_image({'msg_type': 'private', 'number': to, 'msg':name })
                break
            except:
                print(n)
                if n==max_n-1:
                    raise TimeoutError("重试无效")
    except Exception as e:
        print('绘画错误:',e)
        send_msg({'msg_type': 'private', 'number': to, 'msg':'AI绘画操作无法执行'})
        
def remove_parentheses(s):
    result = ""
    skip = False
    for char in s:
        if char in '(（【':
            skip = True
        elif char in ')）】':
            skip = False
        elif not skip:
            result += char
    return result

def poke(user_id,msg_type,id):
    if msg_type=="group":
        res=requests.post(f'http://localhost:{send_port}/group_poke', json={
            'user_id': user_id,
            "group_id":id
        }) 
        print("poke:",user_id,json.loads(res.content))
    else:
        res=requests.post(f'http://localhost:{send_port}/friend_poke', json={
            'user_id': user_id
        }) 
        print("poke:",user_id,json.loads(res.content))

def send_msg(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg'].strip()  # 要回复的消息

    if not os.path.exists(f"./data/msface"):
        os.makedirs(f"./data/msface")
    t_msface_list = os.listdir(f"./data/msface")
    aim_msface_list = []
    for per_t_msface in t_msface_list:
        if per_t_msface in msg:
            aim_msface_list.append(per_t_msface)
    if aim_msface_list and per_t_msface:
        choice_msface = random.choice(aim_msface_list)
    else:
        choice_msface = None
    
    correct = False
    for key_point in ["[","qq","]"]:
        if key_point in msg:
            pass
        else:
            correct=True
    for key_point in ["]你回复"]:
        if key_point in msg:
            pass
        else:
            correct=True

    if msg.strip() and correct:
        if "thinking" in msg and "```" in msg:
            msg="[thinking]"
        if is_filt:
            msg=filted(msg,filted_words)
        if remove_kuohao:
            msg=remove_parentheses(msg)
        msg=strip_chars(msg,"#")
        if msg.strip():
            if msg_type == 'group':
                res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
                    'group_id': number,
                    'message': msg.strip()
                })
                print("send_group_msg:",msg,json.loads(res.content))
                if choice_msface:
                    res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
                        'group_id': number,
                        'message': "[CQ:image,file=http://127.0.0.1:4321/data/msface/%s/%s,subType=1]"%(choice_msface,random.choice(os.listdir(f"./data/msface/{choice_msface}")))
                    })
                    print("send_group_msg:",msg,json.loads(res.content))

            elif msg_type == 'private':
                res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
                    'user_id': number,
                    'message': msg.strip()
                })
                print("send_private_msg:",msg,json.loads(res.content))
                if choice_msface:
                    res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
                        'user_id': number,
                        'message': "[CQ:image,file=http://127.0.0.1:4321/data/msface/%s/%s,subType=1]"%(choice_msface,random.choice(os.listdir(f"./data/msface/{choice_msface}")))
                    })
                    print("send_private_msg:",msg,json.loads(res.content))
            time.sleep(1+random.randrange(0,3))
    return 0

def send_image(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if resp_dict.get("append_data",""):
        append_data = f',{resp_dict.get("append_data","")}'
    else:
        append_data = ''
    if msg_type == 'group':
        res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:image,file=http://127.0.0.1:4321/data/image/%s/%s%s]"%(role,msg,append_data)
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
            'user_id': number,
            'message':"[CQ:image,file=http://127.0.0.1:4321/data/image/%s/%s%s]"%(role,msg,append_data)
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_voice(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:record,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
            'user_id': number,
            'message':"[CQ:record,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_music(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:file,file=http://127.0.0.1:4321/data/voice/%s,name=%s]"%(msg,msg.split("/")[-1].rsplit('.',1)[0][:15]+".wav")
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
            'user_id': number,
            'message': "[CQ:file,file=http://127.0.0.1:4321/data/voice/%s,name=%s]"%(msg,msg.split("/")[-1].rsplit('.',1)[0][:15]+".wav")
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_image_url(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post(f'http://localhost:{send_port}/send_group_msg', json={
            'group_id': number,
            'message': {
                        "type": "image",
                        "data": {
                            "file": "%s"%msg.replace("%20"," ")
                        }
                    }
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post(f'http://localhost:{send_port}/send_private_msg', json={
            'user_id': number,
            'message': {
                        "type": "image",
                        "data": {
                            "file": "%s"%msg
                        }
                    }
        })
        print("send_private_msg:",msg,json.loads(res.content))   

def extract_inf(msg,keyword):
    msglist=[]
    temp_msglist=msg.split("<%s>"%keyword)
    for p_templist in temp_msglist:
        if "</%s>"%keyword in p_templist:
            extractmsg=p_templist.split("</%s>"%keyword)[0]
            chatmsg=p_templist.split("</%s>"%keyword)[1]
            msglist.append({"type":keyword,"content":extractmsg})
            msglist.append({"type":"chat","content":chatmsg})
        else:
            msglist.append({"type":"chat","content":p_templist})
    return msglist

def see_image(msg):
    msglist=extract_inf(msg,"simage")
    chatmsg=""
    for p_msg in msglist:
        if p_msg["type"] == "simage":
            chatmsg+="[图片(需要你提取此图中的所有相关信息)]"
        else:
            chatmsg+=p_msg["content"]
    url = f"http://localhost:{send_port}/get_image"
    returnmsg=""
    for p_msg in msglist:
        if p_msg["type"] == "simage":
            if p_msg["content"].endswith(".jpg"):
                payload = json.dumps({
                    "file": p_msg["content"]
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer 2f68dbbf-519d-4f01-9636-e2421b68f379'
                }
                try:
                    response = requests.request("POST", url, headers=headers, data=payload, timeout=5)
                except:
                    print("下载图片失败")
                    return ""
                print(response.text)
                image = json.loads(response.text)["data"]["file"]
                with open(image, 'rb') as img_file:
                    img_base = base64.b64encode(img_file.read()).decode('utf-8')
                content=[]
                content.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,"+img_base
                                    }
                                        })
                content.append( {
                                    "type": "text",
                                    "text": "\n请根据对话记录相关的信息来详细讲述图片中的内容，以及细节，以下是相关对话记录:“%s”"%chatmsg
                                })

                data={
                        "model": see_model,
                        "messages": [{
                            "role":"system",
                            "content":"设定：“%s”\n现在你的任务是根据上述设定的身份信息来从图片中尽可能详细的识别与设定相关信息"%system_prompt
                        },
                        {"role":"user",
                            "content":content}],
                        "stream": True,
                        "chat_template_kwargs":{
                            "enable_thinking":False
                        },
                        "enable_thinking":False
                    }
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer %s'%see_key
                }
                try:
                    response=requests.post(url=see_url,headers=headers,stream=True,data=json.dumps(data))
                    temp_processed_d_data_image=''
                    for line in response.iter_lines():
                        try:
                            decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                            if decoded != '':
                                temp_processed_d_data_image+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                        except:
                            pass
                    print(temp_processed_d_data_image) 
                except Exception as e:
                    print("视图出错：",e)
                    temp_processed_d_data_image = "动态图片"
                returnmsg+=temp_processed_d_data_image
            else:
                returnmsg+="动态图片"
        else:
            returnmsg+=p_msg["content"]
    # chatmsg="下述涉及图片内容：[%s]\n\n"%temp_processed_d_data_image
    # for p_msg in msglist:
    #     if p_msg["type"] == "simage":
    #         chatmsg+="[图片(上述已给出图片内容)]"
    #     else:
    #         chatmsg+=p_msg["content"]   
    return returnmsg

def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_thinking(text):#去掉思考段内容
    for pthinkkeyword in think_keywords:
        if pthinkkeyword[0] in text:
            if pthinkkeyword[1] not in text.replace(pthinkkeyword[1],"",1):
                continue
            else:
                def extract_think(raw_str,keywords):
                    processed_str=""
                    for keyword in keywords:
                        start_keyword=keyword[0]
                        end_keyword=keyword[1]
                        if start_keyword in raw_str and end_keyword in raw_str:
                            processed_str=raw_str.split(start_keyword,1)[-1].split(end_keyword,1)[0]
                        return processed_str,raw_str.replace(start_keyword+processed_str+end_keyword,"")
                    return "",raw_str
                think_block,text=extract_think(text,think_keywords)
                if debug:
                    print(think_block)
    return text

def choose_model():
    w_c_models=[]
    for c_model in chat_models:
        w_c_models+=[c_model]*c_model["weight"]
    model_info = random.choice(w_c_models)
    if "append_data" not in model_info.keys():
        model_info["append_data"] = {}
    return model_info["model_api"],model_info["model_name"],model_info["model_key"],model_info["append_data"]

def main(rev):
    global objdict
    user_api,user_chat_model,user_key,add_data=choose_model()
    try:
        if not os.path.exists("./user/{role}/all/I_memory.txt"):
            try:
                os.makedirs(f"./user/{role}/all")
            except:
                pass
            with open(f"./user/{role}/all/I_memory.txt","w") as tpass:
                pass
        if not os.path.exists("./data/idname.json"):
            with open("./data/idname.json","w",encoding="utf-8") as tpass:
                tpass.write('{"0":"未知"}')
        timestamp = time.time()
        localtime = time.localtime(timestamp)
        current_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", localtime
            )
        e_information="[information](准确 有时效性)\n当前时间：%s\n"%current_time
        if "sub_type" in rev.keys() and "group_id" in rev.keys():
            if rev["sub_type"] == "poke" and rev['target_id'] == rev['self_id']:
                try:
                    with open("./data/idname.json", 'r', encoding='utf-8') as f:
                        t_gsetting=json.load(f)
                except:
                    t_gsetting={}
                if str(rev['user_id']) in t_gsetting.keys():
                    pokename=t_gsetting[str(rev['user_id'])]
                else:
                    pokename=rev["user_id"]
                    
                rev["raw_message"] = "%s 戳了戳 %s"%(pokename,AI_name)
                rev["message_type"] = "group"
                rev["sender"] = {}
                rev["sender"]["nickname"] = "%s"%pokename
                rev["sender"]["user_id"] = rev["user_id"]
            else:
                
                change_setting("./data/idname.json",str(rev["sender"]["user_id"]),rev["sender"]["nickname"])
        if rev["message_type"] == "private":
            if '自动回复' in rev['raw_message']:
                raise KeyboardInterrupt("自动回复，跳过...")
            if "banaijian%schat"%rev["sender"]["user_id"] not in objdict.keys():
                objdict["banaijian%schat"%rev["sender"]["user_id"]]=""
                objdict["banaijian%smem_i"%rev["sender"]["user_id"]] = MEM_I(AI_name, chat_models[0],f'./user/{role}/p{rev["sender"]["user_id"]}')
            if not os.path.exists(f'./user/{role}/p{rev["sender"]["user_id"]}'):
                os.makedirs(f'./user/{role}/p{rev["sender"]["user_id"]}')
                with open(f'./user/{role}/p{rev["sender"]["user_id"]}/memory.txt',"w") as tpass:
                    pass
            if not os.path.exists(f"./user/{role}/p{rev['sender']['user_id']}/I_memory.txt"):
                with open(f"./user/{role}/p{rev['sender']['user_id']}/I_memory.txt", "w") as tpass:
                    pass
                    
            if not os.path.exists(f"./user/{role}/p{rev['sender']['user_id']}/setting.json"):
                data = {'mood': 'default', 'random_trigger': random_trigger, "root_id": root_ids}
                with open(f"./user/{role}/p{rev['sender']['user_id']}/setting.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            if "[CQ:image,"  not in rev['raw_message']:
                objdict["banaijian%schat"%rev["sender"]["user_id"]]+=(f'‘{rev["sender"]["nickname"]}’'+"说："+rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')+'\n\n')
                objdict["banaijian%schat"%rev["sender"]["user_id"]]=objdict["banaijian%schat"%rev["sender"]["user_id"]][-300:]

            if True:
                a=objdict["banaijian%schat"%rev["sender"]["user_id"]]
                print(a)
                self_id=random.randrange(100000,999999)
                objdict["banaijian%sgeneing"%rev["sender"]["user_id"]]=[self_id] 
                rev['raw_message']=rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')
                if "banaijian%s"%rev["sender"]["user_id"] not in objdict.keys():
                    objdict["banaijian%s"%rev["sender"]["user_id"]]=[[{'role':'system','content':system}]]
                if '#reset' in rev['raw_message']:
                    objdict["banaijian%s"%rev["sender"]["user_id"]]=[[{'role':'system','content':system}]]
                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': '已清空对话历史'}) 
                else:        
                    processed_d_data="强制切换意图"
                    if random.randrange(0,3)==0:#在这里切换情感复原的概率
                        objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]={"role":"system","content":system_prompts["default"]}
                    if weihu:
                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "zzz..."})
                        raise KeyboardInterrupt("维护ing")
                    
                    print(processed_d_data)
                    if not processed_d_data:
                        processed_d_data='.'

                    turl=user_api
                    headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer "+user_key
                        }
                    messages=objdict["banaijian%s"%rev["sender"]["user_id"]][0]+[{"role":"user","content":objdict["banaijian%schat"%rev["sender"]["user_id"]]}]
                    keywords = jieba.analyse.extract_tags(rev['raw_message'].replace(AI_name,""), topK=50)
                    s_memory=get_memory(f"./user/{role}/p{rev['sender']['user_id']}/memory.txt",keywords)
                    s_memory+=get_I_memory(f"./user/{role}/p{rev['sender']['user_id']}/I_memory.txt")
                    _,_,key_result = objdict["banaijian%smem_i"%rev["sender"]["user_id"]].search_querys(keywords, 4, 500)
                    s_memory+=key_result
                    # print(s_memory)
                    data={
                            "model": user_chat_model,##claude-3-opus-vf
                            "messages":merge_contents([{"role":"system","content":messages[0]["content"]+"[memory](模糊 无时效性)\n%s\n"%s_memory+e_information}]+messages[1:]),
                            "stream": True,
                            "use_search": False
                        }
                    data["chat_template_kwargs"] = add_data
                    for key in add_data.keys():
                        data[key] = add_data[key]
                        
                    is_return=True
                    while is_return:
                        is_return=False
                        for _ in range(0,3):
                            try:
                                response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                                if response.status_code==200:
                                    break
                                print("请求错误，尝试兜底模型","model:",data["model"])
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                            except Exception as e:
                                print("请求错误，尝试兜底模型：",e,"model:",data["model"])
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                        is_not_remove_emoji=random.randrange(0,3)#设置清除emoji概率
                        temp_tts_list=[]
                        processed_d_data2=''
                        try:
                            for line in response.iter_lines():
                                try:
                                    decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                                    if decoded != '':
                                        temp_processed_d_data1=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                                        if not temp_processed_d_data1:
                                            continue
                                except Exception as e:
                                    continue
                                    pass
                                if decoded != '':
                                    for p_token in temp_processed_d_data1:
                                        processed_d_data2+=p_token

                                        processed_d_data1=remove_thinking(processed_d_data2)
                                                         
                                        if not is_not_remove_emoji:
                                            processed_d_data1=remove_emojis(processed_d_data1)
                                        lastlen=len(temp_tts_list)
                                        temp_tts_list=processed_d_data1.split("split")
                                        if not temp_tts_list:
                                            temp_tts_list=temp_tts_list[:-1]
                                        if self_id not in objdict["banaijian%sgeneing"%rev["sender"]["user_id"]]:
                                            objdict["banaijian%s"%rev["sender"]["user_id"]][0]=objdict["banaijian%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                                            raise InterruptedError("新消息中断")
                                        
                                        if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                                            if '#voice/' in temp_tts_list[-2]:
                                                try:
                                                    voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                                    if is_tts_v2:
                                                        try:
                                                            emo_vec_str = voice.split("]",1)[0].replace("[","").split(",")
                                                            voice = voice.split("]",1)[-1]
                                                            emo_vec = [float(s) for s in emo_vec_str]
                                                            emo_vec_total = sum(emo_vec)
                                                            emo_vec_norm = [x / (emo_vec_total*2.0) for x in emo_vec]
                                                        except Exception as e:
                                                            print("情绪向量提取失败，采用默认情绪：",e)
                                                            emo_vec = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                                                        data = IndexTTS2RequestData(
                                                                text=voice,
                                                                spk_audio_path=f"voicedata/{speaker}.wav",
                                                                emo_control_method=2,
                                                                emo_vec=emo_vec_norm
                                                            )
                                                        b_wav = requests.post(ttsurls_v2, json=data.to_dict())
                                                    else:
                                                        tts_data = {
                                                            "cha_name": speaker,#这里填本地语音合成包里面配置好的说话人
                                                            "text": voice.replace("...", "…").replace("…", ","),
                                                            "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                                            }
                                                        b_wav = requests.post(
                                                            url=ttsurls, json=tts_data
                                                            )
                                                    n=random.randrange(10000,99999)
                                                    name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                                    to_path='./data/voice/%s'%name
                                                    with open(to_path,'wb') as wbf:
                                                        wbf.write(b_wav.content)
                                                    send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':name })
                                                except Exception as e:
                                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "语音合成失败"})
                                                    print("暂不支持语音合成")
                                            elif "#poke/" in temp_tts_list[-2]:
                                                poke_id=temp_tts_list[-2].split('#poke/')[-1].replace("#",'')
                                                poke(poke_id,"private",None)
                                            elif '#picture/' in temp_tts_list[-2]:
                                                picture=temp_tts_list[-2].split('#picture/')[-1].replace("#",'')
                                                print(picture)
                                                draw_private(picture,rev["sender"]["user_id"])
                                            elif '#searchweb/' in temp_tts_list[-2]:
                                                response.close()
                                                temp_tts_list=temp_tts_list[:-1]
                                                raise KeyboardInterrupt("指令中断")
                                            elif '#searchmemory/' in temp_tts_list[-2]:
                                                response.close()
                                                temp_tts_list=temp_tts_list[:-1]
                                                raise KeyboardInterrupt("指令中断") 
                                            elif '#memory/' in temp_tts_list[-2]:
                                                memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                                print("写入记忆：",memory)    
                                                with open(f"./user/{role}/p{rev['sender']['user_id']}/I_memory.txt", "a", encoding="utf-8") as mem:
                                                    mem.write(" " + memory)
                                                    
                                                with open(f"./user/{role}/all/I_memory.txt", "a", encoding="utf-8") as mem:
                                                    mem.write(" " + memory)

                                                if send_debug:
                                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[写入记忆]"})
                                            elif "#pass/" in temp_tts_list[-2]:
                                                response.close()
                                                if send_debug:
                                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[pass]"})
                                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                            elif "#emotion/" in temp_tts_list[-2]:
                                                t_emotion=temp_tts_list[-2].split("#emotion/")[-1].replace("#",'')
                                                e_image_list=os.listdir(f"./data/image/{role}/{t_emotion}")
                                                e_image=random.choice(e_image_list)
                                                send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%(t_emotion,e_image), 'append_data':'subType=1'})
                                            elif "#mood/" in temp_tts_list[-2]:
                                                t_mood=temp_tts_list[-2].split("#mood/")[-1].replace("#",'')
                                                try:
                                                    objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]={"role":"system","content":system_prompts[t_mood]}
                                                    change_setting(f'./user/{role}/p{rev["sender"]["user_id"]}/setting.json',"mood",t_mood)
                                                    if send_debug:
                                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[%s]"%t_mood})
                                                except Exception as e:
                                                    print("切换情感错误：",e)
                                            elif "#makemusic/" in temp_tts_list[-2]:
                                                t_music_n=temp_tts_list[-2].split("#makemusic/")[-1].replace("#",'')
                                                smusic_l=os.listdir("./data/voice/smusic")
                                                is_find_m=False
                                                for p_music_n in smusic_l:
                                                    if t_music_n in p_music_n:
                                                        is_find_m=True
                                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%p_music_n})
                                                        send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+p_music_n})
                                                        break
                                                if not is_find_m:
                                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                                            elif "#music/" in temp_tts_list[-2]:
                                                t_music_n=temp_tts_list[-2].split("#music/")[-1].replace("#",'')
                                                smusic_l=os.listdir("./data/voice/smusic")
                                                is_find_m=False
                                                for p_music_n in smusic_l:
                                                    if t_music_n in p_music_n:
                                                        is_find_m=True
                                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%p_music_n})
                                                        send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+p_music_n})
                                                        break
                                                if not is_find_m:
                                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                                            else:
                                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-2].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                        except KeyboardInterrupt:
                            print("指令中断")
                        if "抱歉" in temp_tts_list[-1]:
                            objdict["banaijian%s"%rev["sender"]["user_id"]][0]=[objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]]
                            print("催眠失败，重置记忆")
                        else:
                            if '#voice/' in temp_tts_list[-1]:
                                voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                                if is_tts_v2:
                                    try:
                                        emo_vec_str = voice.split("]",1)[0].replace("[","").split(",")
                                        voice = voice.split("]",1)[-1]
                                        emo_vec = [float(s) for s in emo_vec_str]
                                        emo_vec_total = sum(emo_vec)
                                        emo_vec_norm = [x / (emo_vec_total*2.0) for x in emo_vec]
                                    except Exception as e:
                                        print("情绪向量提取失败，采用默认情绪：",e)
                                        emo_vec = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                                    data = IndexTTS2RequestData(
                                            text=voice,
                                            spk_audio_path=f"voicedata/{speaker}.wav",
                                            emo_control_method=2,
                                            emo_vec=emo_vec_norm
                                        )
                                    b_wav = requests.post(ttsurls_v2, json=data.to_dict())
                                else:
                                    tts_data = {
                                        "cha_name": speaker,#这里填本地语音合成包里面配置好的说话人
                                        "text": voice.replace("...", "…").replace("…", ","),
                                        "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                        }
                                    b_wav = requests.post(
                                        url=ttsurls, json=tts_data
                                        )
                                n=random.randrange(10000,99999)
                                name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                to_path='./data/voice/%s'%name
                                with open(to_path,'wb') as wbf:
                                    wbf.write(b_wav.content)
                                send_voice({'msg_type': 'private', 'number':rev["sender"]["user_id"], 'msg':name })
                            elif "#poke/" in temp_tts_list[-1]:
                                poke_id=temp_tts_list[-1].split('#poke/')[-1].replace("#",'')
                                poke(poke_id,"private",None)
                            elif '#picture/' in temp_tts_list[-1]:
                                picture=temp_tts_list[-1].split('#picture/')[-1].replace("#",'')
                                print(picture)
                                draw_private(picture,rev["sender"]["user_id"])
                            elif '#searchweb/' in temp_tts_list[-1]:
                                
                                s_prompt=temp_tts_list[-1].split('#searchweb/')[-1].replace("#",'')
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "正在联网搜索：%s"%s_prompt})
                                search_result=search(s_prompt)
                                print(search_result)
                                objdict["banaijian%s"%rev["sender"]["user_id"]][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2+"""\nsystem[搜索结果不可见]：正在联网搜索：%s\n搜索结果：\n%s\n由于system返回的搜索结果你应该看不见，我将用自己的话详细，具体的讲述一下搜索结果。"""%(s_prompt,search_result)},{"role":"user","content":"开始详细具体的讲述吧"}]
                                messages=objdict["banaijian%s"%rev["sender"]["user_id"]][0]
                                data={
                                    "model": user_chat_model,##claude-3-opus-vf
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False
                                }
                                data["chat_template_kwargs"] = add_data
                                for key in add_data.keys():
                                    data[key] = add_data[key]
                                    
                                is_return=True
                                continue
                            elif '#searchmemory/' in temp_tts_list[-1]:
                                s_prompt=temp_tts_list[-1].split('#searchmemory/')[-1].replace("#",'')
                                if send_debug:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "正在回忆：%s"%s_prompt})
                                tkeywordsm = s_prompt.split(" ")
                                keywordsm=[]
                                for ptkw in tkeywordsm:
                                    if ptkw.replace(" ",""):
                                        keywordsm.append(ptkw)
                                search_result=get_memory(f"./user/{role}/p{rev['sender']['user_id']}/memory.txt",keywordsm,match_n=300, time_n=0, radius=80)
                                search_result += f"\n以下为附加相关信息：\n{objdict['banaijian%smem_i'%rev['sender']['user_id']].agent_search(s_prompt, objdict['banaijian%s'%rev['sender']['user_id']][0])}\n"
                                print(search_result)
                                objdict["banaijian%s"%rev['group_id']][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2+"""\nsystem[记忆检索结果不可见]：记忆检索关键词：%s\n搜索结果：\n%s\n\n现在我已经想起来了相关的记忆，我来重新根据记忆回复一下你吧~"""%(s_prompt,search_result)},{"role":"user","content":"那根据想起来的记忆重新说说吧！"}]
                                messages=objdict["banaijian%s"%rev['group_id']][0]
                                data={
                                    "model": user_chat_model,
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False
                                }
                                data["chat_template_kwargs"] = add_data
                                for key in add_data.keys():
                                    data[key] = add_data[key]
                                    
                                is_return=True
                                continue
                            elif '#memory/' in temp_tts_list[-1]:
                                memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                print("写入记忆：",memory)    
                                with open(f"./user/{role}/p{rev['sender']['user_id']}/I_memory.txt", "a", encoding="utf-8") as mem:
                                    mem.write(" "+memory) 
                                with open(f"./user/{role}/all/I_memory.txt","a",encoding="utf-8") as mem:
                                    mem.write(" "+memory)
                                if send_debug:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[写入记忆]"})
                            elif "#pass/" in temp_tts_list[-1]:
                                if send_debug:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[pass]"})
                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                            elif "#emotion/" in temp_tts_list[-1]:
                                t_emotion=temp_tts_list[-1].split("#emotion/")[-1].replace("#",'')
                                e_image_list=os.listdir(f"./data/image/{role}/{t_emotion}")
                                e_image=random.choice(e_image_list)
                                send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%(t_emotion,e_image), 'append_data':'subType=1'})
                            elif "#mood/" in temp_tts_list[-1]:
                                t_mood=temp_tts_list[-1].split("#mood/")[-1].replace("#",'')
                                try:
                                    objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]={"role":"system","content":system_prompts[t_mood]}
                                    change_setting(f'./user/{role}/p{rev["sender"]["user_id"]}/setting.json',"mood",t_mood)
                                    if send_debug:
                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[%s]"%t_mood})
                                except Exception as e:
                                    print("切换情感错误：",e)
                            elif "#makemusic/" in temp_tts_list[-1]:
                                t_music_n=temp_tts_list[-1].split("#makemusic/")[-1].replace("#",'')
                                smusic_l=os.listdir("./data/voice/smusic")
                                is_find_m=False
                                for p_music_n in smusic_l:
                                    if t_music_n in p_music_n:
                                        is_find_m=True
                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%p_music_n})
                                        send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+p_music_n})
                                        break
                                if not is_find_m:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                            elif "#music/" in temp_tts_list[-1]:
                                t_music_n=temp_tts_list[-1].split("#music/")[-1].replace("#",'')
                                smusic_l=os.listdir("./data/voice/smusic")
                                is_find_m=False
                                for p_music_n in smusic_l:
                                    if t_music_n in p_music_n:
                                        is_find_m=True
                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%t_music_n})
                                        send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+t_music_n})
                                        break
                                if not is_find_m:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                            else:
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-1].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                            if random.randrange(0,30)==0:
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': random.choice(["呜呜，没有零花钱啦...","我亨阔耐，给我钱钱~","有没有好心人给点零花钱，求求啦！"])+"\n[扫码赞助开发者]"})
                                e_image_list=os.listdir(f"./data/image/{role}/money")
                                e_image=random.choice(e_image_list)
                                # send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%("money",e_image)})
                                send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%("money1","money.png")})
                            print(processed_d_data2)
                            objdict["banaijian%s"%rev["sender"]["user_id"]][0]=objdict["banaijian%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2}]
                            with open(
                                    f'./user/{role}/p{rev["sender"]["user_id"]}/memory.txt',
                                    "a",
                                    encoding="utf-8",
                                ) as txt:
                                    timestamp = time.time()
                                    localtime = time.localtime(timestamp)
                                    current_time = time.strftime(
                                        "%Y-%m-%d %H:%M:%S", localtime
                                    )
                                    txt.write(
                                        "[%s]我说：%s\n" % (current_time, rev['raw_message'])
                                    )
                                    txt.write(
                                        "[%s]你回复：%s\n"
                                        % (current_time, processed_d_data1)
                                    )
            print("未发现新消息...运行时间：%f"%(time.time()-startT))
            if len(objdict["banaijian%s"%rev["sender"]["user_id"]][0])> max_turn_private*2+6:
                objdict["banaijian%s"%rev["sender"]["user_id"]][0]=[objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]]+objdict["banaijian%s"%rev["sender"]["user_id"]][0][- max_turn_private*2:]  
                objdict["banaijian%smem_i"%rev["sender"]["user_id"]].add_memory(objdict["banaijian%s"%rev["sender"]["user_id"]][0])
            objdict["banaijian%schat"%rev["sender"]["user_id"]]=''
            

        elif rev["message_type"] == "group":
            
            # raise KeyboardInterrupt("停止群聊...")
            if ("团子" in rev["sender"]["nickname"] or "行己之道" in rev["sender"]["nickname"] or "aaaaa1" in rev["sender"]["nickname"] or rev["sender"]["user_id"] == 3995260769 or rev["sender"]["user_id"] == 3962683856) and "[CQ:image," in rev['raw_message']:
                time.sleep(5+random.randrange(0,5))
                message_id=rev['message_id']
                res=requests.post(f'http://localhost:{send_port}/delete_msg', json={
                    'message_id': message_id,
                })
                print("delete_msg:",rev['raw_message'],json.loads(res.content))
            
            if "吴不爱" in rev["sender"]["nickname"]:
                message_id=rev['message_id']
                res=requests.post(f'http://localhost:{send_port}/delete_msg', json={
                    'message_id': message_id,
                })
                print("delete_msg:",rev['raw_message'],json.loads(res.content))

            pass_ban=False
            
            for ban_name in ban_id_dir.keys():
                if ban_name in str(rev["sender"]["user_id"]) :
                    if time.time()<ban_id_dir[ban_name]:
                        pass_ban = True
                        break
            
            

            if "banaijian%schat"%rev['group_id'] not in objdict.keys():#创建目录
                objdict["banaijian%schat"%rev['group_id']]=""
            if "banaijian%srecap"%rev['group_id'] not in objdict.keys():
                objdict["banaijian%srecap"%rev['group_id']]=""
            if not os.path.exists(f"./user/{role}/g{rev['group_id']}"):
                os.makedirs(f"./user/{role}/g{rev['group_id']}")
                with open(f"./user/{role}/g{rev['group_id']}/memory.txt", "w") as tpass:
                    pass
            if not os.path.exists(f"./user/{role}/g{rev['group_id']}/I_memory.txt"):
                with open(f"./user/{role}/g{rev['group_id']}/I_memory.txt", "w") as tpass:
                    pass
            if not os.path.exists(f"./user/{role}/g{rev['group_id']}/setting.json"):
                data = {'mood': 'default', 'random_trigger': random_trigger, "root_id": root_ids}
                with open(f"./user/{role}/g{rev['group_id']}/setting.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)



            objdict["banaijian%schat"%rev['group_id']]=objdict["banaijian%schat"%rev['group_id']][-550:]
            if "[CQ:image,"  not in rev['raw_message']:#组建单次回复上下文
                objdict["banaijian%schat"%rev['group_id']]+=("["+rev["sender"]["nickname"]+",qq:%s]说：“"%rev["sender"]["user_id"]+rev['raw_message'].replace('[CQ:at,qq=%d,name=%s]'%(rev['self_id'],AI_name),"")+'”\n\n')
            else:
                objdict["banaijian%schat"%rev['group_id']]+=("["+rev["sender"]["nickname"]+",qq:%s]发送了一张图片：“<simage>"%rev["sender"]["user_id"]+rev['raw_message'][15:51]+'</simage>”\n\n')

            for pban_name in ban_names:
                if pban_name in rev["sender"]["nickname"] or str(pban_name) == str(rev["sender"]["user_id"]):
                    pass_ban = True
                    break
            if pass_ban:
                raise RuntimeError("break limitless turn")#屏蔽指定名称qq
            if "#settitle:" in rev['raw_message']:#自动设置头衔（暂时无效）
                title=rev['raw_message'].split(':',1)[-1][:5]
                res=requests.post(f'http://localhost:{send_port}/set_group_special_title', json={
                    'group_id': rev['group_id'],
                    'user_id': rev['user_id'],
                    'special_title':title,
                    'duration':-1
                })
                print("set_group_special_title:",rev['raw_message'].split(':',1)[-1][:5],json.loads(res.content))
            with open(f"./user/{role}/g{rev['group_id']}/setting.json", 'r', encoding='utf-8') as f:
                tt_gsetting=json.load(f)
            tt_random_trigger=tt_gsetting["random_trigger"]
            root_id=tt_gsetting["root_id"]
            now_mood=tt_gsetting["mood"]
            if "is_ban" not in tt_gsetting.keys():#补全缺失内容
                tt_gsetting["is_ban"]=False
                with open(f"./user/{role}/g{rev['group_id']}/setting.json", 'w', encoding='utf-8') as f:
                    json.dump(tt_gsetting, f, ensure_ascii=False, indent=4)
            else:
                is_ban=tt_gsetting["is_ban"]
            is_trigger=False#比对触发词
            for trigger in triggers:
                if trigger in rev['raw_message']:
                    is_trigger = True
                    break
            if rev['group_id'] in [308228675] and "#msg#" in rev['raw_message']:
                if "#end#" in rev["raw_message"]:
                    with open(r"D:\program-illusion\illueU\frp\autorestart\order.txt","w",encoding="utf-8") as ft:
                                    ft.write("end")
                    print("直播下播")
                elif "#clear#" in rev["raw_message"]:
                    with open(r"D:\program-illusion\blivebot\temp\control.txt","w",encoding="utf-8") as ft:
                                    ft.write("clear")
                    print("直播清除记忆")
                elif "#order#" in rev["raw_message"]:
                    torder=rev["raw_message"].split("#order#")[-1]
                    def send_command(command, username="python_client",BASE_URL="http://192.168.3.1:8081"):
                        """
                        发送命令到AltoClef（类似whisper功能）
                        
                        参数：
                            command (str): 要执行的命令，如 "get diamond 5"
                            username (str): 发送命令的用户名
                            
                        返回：
                            dict: 服务器响应
                        """
                        try:
                            HEADERS = {
    "Content-Type": "application/json; charset=utf-8" # Explicitly set charset
}
                            # 构建请求数据
                            data = {
                                "command": command,
                                "username": username
                            }
                            
                            # 发送POST请求
                            response = requests.post(
                                f"{BASE_URL}/command",
                                headers=HEADERS,
                                data=json.dumps(data, ensure_ascii=False) # Let requests handle encoding
                            )
                            
                            if response.status_code == 200:
                                return response.json()
                            else:
                                print(f"发送命令失败，状态码：{response.status_code}")
                                return None
                        except Exception as e:
                            print(f"发送命令时发生错误：{str(e)}")
                            return None
                    send_command(torder)
                user_msg =rev['raw_message'].replace("#msg#","")
                datam={"name":"幻蓝","content":user_msg,"key":"sk-pqq","mod":"speak"}
                response_raw = requests.post(url="http://127.0.0.1:18871/msg",data=json.dumps(datam)).content
                response=json.loads(response_raw)['response']
                if response=="ok":
                    print("发送成功")
                else:
                    print("发送出错：",response)
            elif (is_trigger or '[CQ:at,qq=%d]'%rev['self_id'] in rev['raw_message'] or random.randrange(0,tt_random_trigger)==0):#触发回复
                a=objdict["banaijian%schat"%rev['group_id']]
                print(a)
                self_id=random.randrange(100000,999999)
                objdict["banaijian%sgeneing"%rev['group_id']]=[self_id] 
                time.sleep(0.5)
                rev['raw_message']=rev['raw_message'].replace('[CQ:at,qq=%d,name=%s]'%(rev['self_id'],AI_name),'')
                if "banaijian%s"%rev['group_id'] not in objdict.keys():
                    objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                    objdict["banaijian%smem_i"%rev['group_id']] = MEM_I(AI_name, chat_models[0],f"./user/{role}/g{rev['group_id']}")
                if '#reset' in rev['raw_message']:
                    objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[已清空对话历史]'}) 
                elif "#new_soup" in rev['raw_message']:
                    objdict["banaijian%ssoup_agent"%rev['group_id']]=TurtleSoupHost(config_path="soups.json")
                    soup_info = objdict["banaijian%ssoup_agent"%rev['group_id']].get_current_soup_info_text()
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f'开启新的海龟汤\n{soup_info}'}) 
                elif "#ask_soup" in rev['raw_message']:
                    if "banaijian%ssoup_agent"%rev['group_id'] not in objdict.keys():
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f'当前无正在进行的海龟汤'}) 
                    soup_reply = objdict["banaijian%ssoup_agent"%rev['group_id']].handle_turn(rev["raw_message"].split("#ask_soup")[-1])
                    if "正确" == soup_reply:
                        soup_bottom = objdict["banaijian%ssoup_agent"%rev['group_id']].get_soup_bottom()
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f'恭喜你通关本海龟汤\n汤底如下：\n{soup_bottom}'}) 
                    else:
                        objdict["banaijian%ssoup_agent"%rev['group_id']].record_turn(rev["raw_message"].split("#ask_soup")[-1], soup_reply)
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f'{soup_reply}'}) 
                elif "#mood" in rev['raw_message'] and rev['user_id'] in root_id:
                    for tt_mood in system_prompts.keys():
                        if tt_mood in rev['raw_message'].replace("#mood",""):
                            objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system_prompts[tt_mood]}]]
                            change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","mood",tt_mood)
                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[%s]'%tt_mood}) 
                            break
                elif "#forcememory" in rev['raw_message'] and rev['user_id'] in root_id:
                    force_memory = rev['raw_message'].split("#forcememory")[-1]
                    with open(f"./user/{role}/g{rev['group_id']}/I_memory.txt", "a", encoding="utf-8") as mem:
                        mem.write(" " + force_memory)
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[强制写入记忆]'}) 

                elif "#forceallmemory" in rev['raw_message'] and rev['user_id'] in root_ids:
                    force_memory = rev['raw_message'].split("#forceallmemory")[-1]
                    user_list_m = os.listdir("./user")
                    for per_user_m in user_list_m:
                        with open(f"./user/{role}/{per_user_m}/I_memory.txt", "a", encoding="utf-8") as mem:
                            mem.write(" " + force_memory)
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[全频道写入记忆]'})

                elif "#addid" in rev['raw_message'] and rev['user_id'] in root_id:
                    addid=rev['raw_message'].split("#addid")[-1]
                    root_id.append(int(addid.replace(" ","")))
                    change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","root_id",root_id)  
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[添加管理员ID]'})      
                elif "#random" in rev['raw_message'] and rev['user_id'] in root_id:
                    t_random_trigger=int(rev['raw_message'].split(" ")[-1])
                    change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","random_trigger",t_random_trigger)
                    if t_random_trigger<=0:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[已关机]'}) 
                    else:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[触发率设置为1/%d]'%t_random_trigger}) 
                elif "#ban" in rev['raw_message'] and rev['user_id'] in root_id:
                    is_ban=int(rev['raw_message'].split(" ")[-1])
                    if is_ban in [0,1,2]:
                        change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","is_ban",is_ban)
                        if is_ban==0:
                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[已关闭禁言能力]'}) 
                        else:
                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[已禁言等级设为%d]'%is_ban}) 
                

                else:        
                    if tt_random_trigger < 1:
                        raise KeyboardInterrupt("群聊已停止回复")
                    
                    processed_d_data="强制切换意图"
                    turl=user_api
                    # if rev['group_id'] != 930214132 and jieyue:
                    #     # send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[illue quota is not enough]"})
                    #     # raise KeyboardInterrupt("节约token")
                    #     user_key="sk-OBOxTsNA8Gz9DuMQAc4669399f7a4b3fAaE3Ee91C2068d0f"
                    #     user_chat_model="gpt-4o"
                    #     turl="http://154.37.221.52:3000/v1/chat/completions"
                    if random.randrange(0,10)==0:#在这里切换情感复原的概率
                        objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts["default"]}
                    if weihu:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[zzz...]"})
                        raise KeyboardInterrupt("维护ing")
                    print(processed_d_data)
                    if not processed_d_data:
                        processed_d_data='.'
                    turl=user_api
                    headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer "+user_key
                        }
                    temp_raw_msg=objdict["banaijian%schat"%rev['group_id']]
                    
                    if "<simage>" in temp_raw_msg and "</simage>" in temp_raw_msg:
                        temp_raw_msg = see_image(temp_raw_msg)
                    messages=objdict["banaijian%s"%rev['group_id']][0]
                    keywords = jieba.analyse.extract_tags(rev['raw_message'].replace(AI_name,""), topK=200)
                    s_memory=get_memory(f"./user/{role}/g{rev['group_id']}/memory.txt",keywords,match_n=500)
                    s_memory+=get_I_memory(f"./user/{role}/g{rev['group_id']}/I_memory.txt")
                    _,_,key_result = objdict["banaijian%smem_i"%rev['group_id']].search_querys(keywords, 4, 500)
                    s_memory+=key_result
                    # print(s_memory)
                    temp_system_content = messages[0]["content"]+"[memory](模糊 无时效性)\n%s\n"%s_memory+'''\n%s\n'''%objdict["banaijian%srecap"%rev['group_id']]+e_information
                    if enable_think:
                        think_enhance_prompt = enhance_response(make_enhance_system_prompt(temp_system_content,AI_name),messages[-max_turn_group*10:],temp_raw_msg,AI_name,think_url,think_model,think_key)
                        print(think_enhance_prompt)
                    else:
                        think_enhance_prompt = ""
                    objdict["banaijian%schat"%rev['group_id']]=''
                    messages1=messages+[{"role":"user","content":f"{random.choice(['（请只提及和回复来自qq的内容，不可说其他废话和编造虚构内容）','','',''])}\n{think_enhance_prompt}\n\n<qq>\n{temp_raw_msg}\n</qq>"}]
                    data={
                            "model": user_chat_model,
                            "messages":merge_contents([{"role":"system","content":temp_system_content}]+messages1[-max_turn_group*2 if len(messages1)>max_turn_group*2+1 else 1:]),
                            "stream": True,
                            # "enable_thinking":False
                        }
                    data["chat_template_kwargs"] = add_data
                    for key in add_data.keys():
                        data[key] = add_data[key]
                        
                    messages+=[{"role":"user","content":f"<qq>\n{temp_raw_msg}\n</qq>"}]
                    is_return=True
                    while is_return:
                        is_return=False
                        for _ in range(0,3):
                            try:
                                response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                                if response.status_code==200:
                                    break
                                print("请求错误，尝试兜底模型",response.content.decode("utf-8"),"model:",data["model"])
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                            except Exception as e:
                                print("请求错误，尝试兜底模型：",e,"model:",data["model"])
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                        is_not_remove_emoji=random.randrange(0,3)#设置清除emoji概率
                        temp_tts_list=[]
                        processed_d_data2=''
                        try:
                            for line in response.iter_lines():
                                try:
                                    decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                                    if decoded != '':
                                        temp_processed_d_data1=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                                        if not temp_processed_d_data1:
                                            continue
                                except Exception as e:
                                    print(decoded,e)
                                    continue
                                    pass
                                if decoded != '':
                                    for p_token in temp_processed_d_data1:
                                        processed_d_data2+=p_token

                                        processed_d_data1=remove_thinking(processed_d_data2)

                                        if not is_not_remove_emoji:
                                            processed_d_data1=remove_emojis(processed_d_data1)
                                        lastlen=len(temp_tts_list)
                                        temp_tts_list=processed_d_data1.split("split")
                                        if not temp_tts_list:
                                            temp_tts_list=temp_tts_list[:-1]
                                        
                                        
                                        if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                                            if '#voice/' in temp_tts_list[-2]:
                                                try:
                                                    voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                                    if is_tts_v2:
                                                        try:
                                                            emo_vec_str = voice.split("]",1)[0].replace("[","").split(",")
                                                            voice = voice.split("]",1)[-1]
                                                            emo_vec = [float(s) for s in emo_vec_str]
                                                            emo_vec_total = sum(emo_vec)
                                                            emo_vec_norm = [x / (emo_vec_total*2.0) for x in emo_vec]
                                                        except Exception as e:
                                                            print("情绪向量提取失败，采用默认情绪：",e)
                                                            emo_vec = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                                                        data = IndexTTS2RequestData(
                                                                text=voice,
                                                                spk_audio_path=f"voicedata/{speaker}.wav",
                                                                emo_control_method=2,
                                                                emo_vec=emo_vec_norm
                                                            )
                                                        b_wav = requests.post(ttsurls_v2, json=data.to_dict())
                                                    else:
                                                        tts_data = {
                                                            "cha_name": speaker,#这里填本地语音合成包里面配置好的说话人
                                                            "text": voice.replace("...", "…").replace("…", ","),
                                                            "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                                            }
                                                        b_wav = requests.post(
                                                            url=ttsurls, json=tts_data
                                                            )
                                                    n=random.randrange(10000,99999)
                                                    name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                                    to_path='./data/voice/%s'%name
                                                    with open(to_path,'wb') as wbf:
                                                        wbf.write(b_wav.content)
                                                    send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':name })
                                                except Exception as e:
                                                    print("暂不支持语音合成")
                                            elif "#poke/" in temp_tts_list[-2]:
                                                poke_id=temp_tts_list[-2].split('#poke/')[-1].replace("#",'')
                                                poke(poke_id,"group",rev['group_id'])
                                            elif '#picture/' in temp_tts_list[-2]:
                                                picture=temp_tts_list[-2].split('#picture/')[-1].replace("#",'')
                                                print(picture)
                                                draw_group(picture,rev['group_id'])
                                            elif '#searchweb/' in temp_tts_list[-2]:
                                                response.close()
                                                temp_tts_list=temp_tts_list[:-1]
                                                raise KeyboardInterrupt("指令中断")
                                            elif '#searchmemory/' in temp_tts_list[-2]:
                                                response.close()
                                                temp_tts_list=temp_tts_list[:-1]
                                                raise KeyboardInterrupt("指令中断")
                                            elif '#memory/' in temp_tts_list[-2]:
                                                memory=temp_tts_list[-2].split('#memory/')[-1].replace("#",'')
                                                print("写入记忆：",memory)    
                                                with open(f"./user/{role}/g{rev['group_id']}/I_memory.txt","a",encoding="utf-8") as mem:
                                                    mem.write(" "+memory)
                                                with open(f"./user/{role}/all/I_memory.txt","a",encoding="utf-8") as mem:
                                                    mem.write(" "+memory)
                                                if send_debug:
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[写入记忆]"})
                                            elif "#pass/" in temp_tts_list[-2]:
                                                response.close()
                                                if send_debug:
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[pass]"})
                                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                            elif "#emotion/" in temp_tts_list[-2]:
                                                t_emotion=temp_tts_list[-2].split("#emotion/")[-1].replace("#",'')
                                                e_image_list=os.listdir(f"./data/image/{role}/{t_emotion}")
                                                e_image=random.choice(e_image_list)
                                                send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%(t_emotion,e_image), 'append_data':'subType=1'})
                                            elif "#mood/" in temp_tts_list[-2]:
                                                t_mood=temp_tts_list[-2].split("#mood/")[-1].replace("#",'')
                                                try:
                                                    objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts[t_mood]}
                                                    change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","mood",t_mood)
                                                    if send_debug:
                                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[%s]"%t_mood})
                                                except Exception as e:
                                                    print("切换情感错误：",e)
                                            elif "#do/" in temp_tts_list[-2]:
                                                response.close()
                                                temp_tts_list=temp_tts_list[:-1]
                                                raise KeyboardInterrupt("指令中断")
                                            elif "#ban/" in temp_tts_list[-2]:
                                                t_ban=temp_tts_list[-2].split("#ban/")[-1].replace("#",'')
                                                ban_id = t_ban.split("-")[0]
                                                ban_time = int(t_ban.split("-")[-1])
                                                if is_ban==2 or (is_ban==1 and now_mood == "angry") or ban_time==0:
                                                    if ban_time>60:
                                                        ban_time=60
                                                    res=requests.post(f'http://localhost:{send_port}/set_group_ban', json={
                                                        'group_id': rev['group_id'],
                                                        'user_id': ban_id,
                                                        'duration': ban_time*60
                                                    })
                                                    if ban_time==0:
                                                        ban_id_dir[ban_id]=time.time()+ban_time*60
                                                        try:
                                                            with open("./data/idname.json", 'r', encoding='utf-8') as f:
                                                                t_gsetting=json.load(f)
                                                        except:
                                                            t_gsetting={}
                                                        if str(ban_id) in t_gsetting.keys():
                                                            bname=t_gsetting[str(ban_id)]
                                                        else:
                                                            bname=ban_id
                                                        if send_debug:
                                                            if ban_time:
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[屏蔽%s:%d分钟]"%(bname,ban_time)})
                                                            else:
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[解除屏蔽%s]"%(bname)})
                                                        if ban_time:
                                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "%s，不理你了！"%(bname)})
                                                        else:
                                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "继续聊天吧，%s"%(bname)})
                                                else:
                                                    ban_id_dir[ban_id]=time.time()+ban_time*60
                                                    try:
                                                        with open("./data/idname.json", 'r', encoding='utf-8') as f:
                                                            t_gsetting=json.load(f)
                                                    except:
                                                        t_gsetting={}
                                                    if str(rev['target_id']) in t_gsetting.keys():
                                                        bname=t_gsetting[str(ban_id)]
                                                    else:
                                                        bname=ban_id
                                                    if send_debug:
                                                        if ban_time:
                                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[屏蔽%s:%d分钟]"%(bname,ban_time)})
                                                        else:
                                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[解除屏蔽%s]"%(bname)})
                                                    if ban_time:
                                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "%s，不理你了！"%(bname)})
                                                    else:
                                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "继续聊天吧，%s"%(bname)})
                                            elif "#makemusic/" in temp_tts_list[-2]:
                                                if cpu_lacking:
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "算力不足，暂关闭唱歌，可前往直播间点歌"})
                                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                                music_data_list=temp_tts_list[-2].split("#makemusic/")[-1].replace("#",'')
                                                t_music_n = music_data_list.split("&")[0]
                                                t_misic_prompt = music_data_list.split("&")[1]
                                                t_misic_reference_name = music_data_list.split("&")[2]
                                                t_music_lyric = music_data_list.split("&")[-1]
                                                datam={"name":t_music_n,"speaker":singer,"low":True,"generate_music_first": True,"reference_audio_name": t_misic_reference_name,"prompt":t_misic_prompt,"lyrics":t_music_lyric}
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"开始创作《{t_music_n}》\n{t_misic_prompt}"})
                                                response1 = requests.post(url=song_url,data=json.dumps(datam),stream=True) 
                                                for line in response1.iter_lines():
                                                    decoded = (
                                                        line.decode("unicode_escape")
                                                        .replace("\b", "\\b")
                                                        .replace("\f", "\\f")
                                                        .replace("\r", "\\r")
                                                        .replace("\t", "\\t")
                                                        .replace("\n", "\\n")
                                                    )
                                                    done = json.loads(decoded)["done"]
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"《{t_music_n}》\n灵感：{t_misic_reference_name}\n\n{t_music_lyric}"})
                                                    if done == 100:
                                                        file_name = json.loads(decoded)["name"]
                                                        if "error:" in file_name:
                                                            w_error = file_name.replace("error:","")
                                                            if w_error == "time":
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，原因：歌曲过长"})
                                                            else:
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，错误码：%s"%w_error})
                                                        else:
                                                            with open("./data/voice/smusic/%s"%file_name, "wb") as f:
                                                                response_wav = requests.get(url=f"{song_url}/output/{file_name}").content
                                                                f.write(response_wav)
                                                            # copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                                            requests.post(url=f"{song_url}/removea/{file_name}",stream=True) 
                                                            send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                                            time.sleep(random.randrange(0,3))
                                                            send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                            elif "#music/" in temp_tts_list[-2]:
                                                if cpu_lacking:
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "算力不足，暂关闭唱歌，可前往直播间点歌"})
                                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                                t_music_n=temp_tts_list[-2].split("#music/")[-1].replace("#",'')
                                                
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：0%"})
                                                datam={"name":t_music_n,"speaker":singer,"low":True}
                                                response1 = requests.post(url=song_url,data=json.dumps(datam),stream=True)
                                                for line in response1.iter_lines():
                                                    decoded = (
                                                        line.decode("unicode_escape")
                                                        .replace("\b", "\\b")
                                                        .replace("\f", "\\f")
                                                        .replace("\r", "\\r")
                                                        .replace("\t", "\\t")
                                                        .replace("\n", "\\n")
                                                    )
                                                    done = json.loads(decoded)["done"]
                                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：{done}%"})
                                                    if done == 100:
                                                        file_name = json.loads(decoded)["name"]
                                                        if "error:" in file_name:
                                                            w_error = file_name.replace("error:","")
                                                            if w_error == "time":
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，原因：歌曲过长"})
                                                            else:
                                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，错误码：%s"%w_error})
                                                        else:
                                                            with open("./data/voice/smusic/%s"%file_name, "wb") as f:
                                                                response_wav = requests.get(url=f"{song_url}/output/{file_name}").content
                                                                f.write(response_wav)
                                                            #copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                                            requests.post(url=f"{song_url}/removea/{file_name}",stream=True) 
                                                            send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                                            time.sleep(random.randrange(0,3))
                                                            send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                                    #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[未找到合适歌曲]"})
                                            else:
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-2].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                                                print("当前模型：",data["model"])
                                            if self_id not in objdict["banaijian%sgeneing"%rev['group_id']]:
                                                objdict["banaijian%s"%rev['group_id']][0]=objdict["banaijian%s"%rev['group_id']][0]+[{'role':'user','content':temp_raw_msg},{'role':'assistant','content':processed_d_data1.replace(temp_tts_list[-1],"")}]
                                                with open(
                                                    f"./user/{role}/g{rev['group_id']}/memory.txt",
                                                    "a",
                                                    encoding="utf-8",
                                                ) as txt:
                                                    timestamp = time.time()
                                                    localtime = time.localtime(timestamp)
                                                    current_time = time.strftime(
                                                        "%Y-%m-%d %H:%M:%S", localtime
                                                    )
                                                    txt.write(
                                                        "[%s]%s\n" % (current_time, temp_raw_msg)
                                                    )
                                                    txt.write(
                                                        "[%s]你回复：%s\n"
                                                        % (current_time, processed_d_data1)
                                                    )
                                                raise InterruptedError("新消息中断")
                        except KeyboardInterrupt:
                            print("指令中断")
                        if "抱歉" in temp_tts_list[-1]:
                            # objdict["banaijian%s"%rev['group_id']][0]=[objdict["banaijian%s"%rev['group_id']][0][0]]
                            # print("催眠失败，重置记忆")
                            pass
                        else:
                            if '#voice/' in temp_tts_list[-1]:
                                voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                                
                                if is_tts_v2:
                                    try:
                                        emo_vec_str = voice.split("]",1)[0].replace("[","").split(",")
                                        voice = voice.split("]",1)[-1]
                                        emo_vec = [float(s) for s in emo_vec_str]
                                        emo_vec_total = sum(emo_vec)
                                        emo_vec_norm = [x / (emo_vec_total*2.0) for x in emo_vec]
                                    except Exception as e:
                                        print("情绪向量提取失败，采用默认情绪：",e)
                                        emo_vec = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
                                    data = IndexTTS2RequestData(
                                            text=voice,
                                            spk_audio_path=f"voicedata/{speaker}.wav",
                                            emo_control_method=2,
                                            emo_vec=emo_vec_norm
                                        )
                                    b_wav = requests.post(ttsurls_v2, json=data.to_dict())
                                else:
                                    tts_data = {
                                        "cha_name": speaker,#这里填本地语音合成包里面配置好的说话人
                                        "text": voice.replace("...", "…").replace("…", ","),
                                        "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                        }
                                    b_wav = requests.post(
                                        url=ttsurls, json=tts_data
                                        )
                                n=random.randrange(10000,99999)
                                name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                to_path='./data/voice/%s'%name
                                with open(to_path,'wb') as wbf:
                                    wbf.write(b_wav.content)
                                send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':name })
                            elif "#poke/" in temp_tts_list[-1]:
                                poke_id=temp_tts_list[-1].split('#poke/')[-1].replace("#",'')
                                poke(poke_id,"group",rev['group_id'])
                            elif '#picture/' in temp_tts_list[-1]:
                                picture=temp_tts_list[-1].split('#picture/')[-1].replace("#",'')
                                print(picture)
                                draw_group(picture,rev['group_id'])
                            elif '#searchweb/' in temp_tts_list[-1]:

                                s_prompt=temp_tts_list[-1].split('#searchweb/')[-1].replace("#",'')
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "正在联网搜索：%s"%s_prompt})
                                search_result=search(s_prompt)
                                print(search_result)
                                objdict["banaijian%s"%rev['group_id']][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2+"""\nsystem[搜索结果不可见]：正在联网搜索：%s\n搜索结果：\n%s\n由于system返回的搜索结果你应该看不见，我将用自己的话详细，具体的讲述一下搜索结果。"""%(s_prompt,search_result)},{"role":"user","content":"开始详细具体的讲述吧"}]
                                messages=objdict["banaijian%s"%rev['group_id']][0]
                                data={
                                    "model": user_chat_model,
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False,
                                    # "enable_thinking":False
                                }
                                data["chat_template_kwargs"] = add_data
                                for key in add_data.keys():
                                    data[key] = add_data[key]
                                    
                                is_return=True
                                continue
                            elif '#searchmemory/' in temp_tts_list[-1]:

                                s_prompt=temp_tts_list[-1].split('#searchmemory/')[-1].replace("#",'')
                                
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "正在回忆：%s"%s_prompt})
                                tkeywordsm = s_prompt.split(" ")
                                keywordsm=[]
                                for ptkw in tkeywordsm:
                                    if ptkw.replace(" ",""):
                                        keywordsm.append(ptkw)
                                search_result=get_memory(f"./user/{role}/g{rev['group_id']}/memory.txt",keywordsm,match_n=300, time_n=0, radius=120, length=4096000)
                                search_result += f"\n以下为附加相关信息：\n{objdict['banaijian%smem_i'%rev['group_id']].agent_search(s_prompt, objdict['banaijian%s'%rev['group_id']][0])}\n"
                                print(search_result)
                                objdict["banaijian%s"%rev['group_id']][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2+"""\nsystem[记忆检索结果不可见]：记忆检索关键词：%s\n搜索结果：\n%s\n\n现在我已经想起来了相关的记忆，我来重新根据记忆回复一下你吧~"""%(s_prompt,search_result)},{"role":"user","content":"那根据想起来的记忆重新说说吧！"}]
                                messages=objdict["banaijian%s"%rev['group_id']][0]
                                data={
                                    "model": user_chat_model,
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日在不？#split#”\n"+e_information}]+messages[-max_turn_group*2 if len(messages1)>max_turn_group*2+1 else 1:]),
                                    "stream": True,
                                    "use_search": False
                                }
                                data["chat_template_kwargs"] = add_data
                                for key in add_data.keys():
                                    data[key] = add_data[key]
                                    
                                is_return=True
                                continue
                            elif '#do/' in temp_tts_list[-1]:

                                s_prompt=temp_tts_list[-1].split('#do/')[-1].replace("#",'')
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "执行操作：%s"%s_prompt})
                                search_result=search(s_prompt)
                                print(search_result)
                                objdict["banaijian%s"%rev['group_id']][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data2+"""Agent助手开始执行操作“%s”\nAgent助手执行操作返回：无法获取有关信息，操作未成功执行"""%s_prompt},{"role":"user","content":"<system>暂时无法使用Agent助手，请停止使用此指令</system>"}]
                                messages=objdict["banaijian%s"%rev['group_id']][0]
                                data={
                                    "model": user_chat_model,
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False,
                                    # "enable_thinking":False
                                }
                                data["chat_template_kwargs"] = add_data
                                for key in add_data.keys():
                                    data[key] = add_data[key]
                                    
                                is_return=True
                                continue
                            elif '#memory/' in temp_tts_list[-1]:
                                memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                print("写入记忆：",memory)    
                                with open(f"./user/{role}/g{rev['group_id']}/I_memory.txt","a",encoding="utf-8") as mem:
                                    mem.write(" "+memory)
                                with open(f"./user/{role}/all/I_memory.txt","a",encoding="utf-8") as mem:
                                    mem.write(" "+memory)
                                if send_debug:
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[写入记忆]"})
                            elif "#pass/" in temp_tts_list[-1]:
                                if send_debug:
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[pass]"})
                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                            elif "#emotion/" in temp_tts_list[-1]:
                                t_emotion=temp_tts_list[-1].split("#emotion/")[-1].replace("#",'')
                                e_image_list=os.listdir(f"./data/image/{role}/{t_emotion}")
                                e_image=random.choice(e_image_list)
                                send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%(t_emotion,e_image), 'append_data':'subType=1'})
                            elif "#mood/" in temp_tts_list[-1]:
                                t_mood=temp_tts_list[-1].split("#mood/")[-1].replace("#",'')
                                try:
                                    objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts[t_mood]}
                                    change_setting(f"./user/{role}/g{rev['group_id']}/setting.json","mood",t_mood)
                                    if send_debug:
                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[%s]"%t_mood})
                                except Exception as e:
                                    print("切换情感错误：",e)
                            elif "#ban/" in temp_tts_list[-1]:
                                t_ban=temp_tts_list[-1].split("#ban/")[-1].replace("#",'')
                                ban_id = t_ban.split("-")[0]
                                ban_time = int(t_ban.split("-")[-1])
                                if is_ban==2 or (is_ban==1 and now_mood == "angry") or ban_time==0:
                                    if ban_time>60:
                                        ban_time=60
                                    res=requests.post(f'http://localhost:{send_port}/set_group_ban', json={
                                        'group_id': rev['group_id'],
                                        'user_id': ban_id,
                                        'duration': ban_time*60
                                    })
                                    if ban_time==0:
                                        ban_id_dir[ban_id]=time.time()+ban_time*60
                                        try:
                                            with open("./data/idname.json", 'r', encoding='utf-8') as f:
                                                t_gsetting=json.load(f)
                                        except:
                                            t_gsetting={}
                                        if str(ban_id) in t_gsetting.keys():
                                            bname=t_gsetting[str(ban_id)]
                                        else:
                                            bname=ban_id
                                        if send_debug:
                                            if ban_time:
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[屏蔽%s:%d分钟]"%(bname,ban_time)})
                                            else:
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[解除屏蔽%s]"%(bname)})
                                        if ban_time:
                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "%s，不理你了！"%(bname)})
                                        else:
                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "继续聊天吧，%s"%(bname)})
                                else:
                                    ban_id_dir[ban_id]=time.time()+ban_time*60
                                    try:
                                        with open("./data/idname.json", 'r', encoding='utf-8') as f:
                                            t_gsetting=json.load(f)
                                    except:
                                        t_gsetting={}
                                    if str(rev['target_id']) in t_gsetting.keys():
                                        bname=t_gsetting[str(ban_id)]
                                    else:
                                        bname=ban_id
                                    if send_debug:
                                        if ban_time!="0":
                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[屏蔽%s:%d分钟]"%(bname,ban_time)})
                                        else:
                                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[解除屏蔽%s]"%(bname)})
                                    if ban_time:
                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "%s，不理你了！"%(bname)})
                                    else:
                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "继续聊天吧，%s"%(bname)})
                            elif "#makemusic/" in temp_tts_list[-1]:
                                if cpu_lacking:
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "算力不足，暂关闭唱歌，可前往直播间点歌"})
                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                music_data_list=temp_tts_list[-1].split("#makemusic/")[-1].replace("#",'')
                                t_music_n = music_data_list.split("&")[0]
                                t_misic_prompt = music_data_list.split("&")[1]
                                t_misic_reference_name = music_data_list.split("&")[2]
                                t_music_lyric = music_data_list.split("&")[-1]
                                datam={"name":t_music_n,"speaker":singer,"low":True,"generate_music_first": True,"reference_audio_name": t_misic_reference_name,"prompt":t_misic_prompt,"lyrics":t_music_lyric}
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"开始创作《{t_music_n}》\n{t_misic_prompt}"})
                                response1 = requests.post(url=song_url,data=json.dumps(datam),stream=True) 
                                for line in response1.iter_lines():
                                    decoded = (
                                        line.decode("unicode_escape")
                                        .replace("\b", "\\b")
                                        .replace("\f", "\\f")
                                        .replace("\r", "\\r")
                                        .replace("\t", "\\t")
                                        .replace("\n", "\\n")
                                    )
                                    done = json.loads(decoded)["done"]
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"《{t_music_n}》\n灵感：{t_misic_reference_name}\n\n{t_music_lyric}"})
                                    if done == 100:
                                        file_name = json.loads(decoded)["name"]
                                        if "error:" in file_name:
                                            w_error = file_name.replace("error:","")
                                            if w_error == "time":
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，原因：歌曲过长"})
                                            else:
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，错误码：%s"%w_error})
                                        else:
                                            with open("./data/voice/smusic/%s"%file_name, "wb") as f:
                                                response_wav = requests.get(url=f"{song_url}/output/{file_name}").content
                                                f.write(response_wav)
                                            # copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                            requests.post(url=f"{song_url}/removea/{file_name}",stream=True) 
                                            send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                            time.sleep(random.randrange(0,3))
                                            send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                            elif "#music/" in temp_tts_list[-1]:
                                if cpu_lacking:
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "算力不足，暂关闭唱歌，可前往直播间点歌"})
                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                t_music_n=temp_tts_list[-1].split("#music/")[-1].replace("#",'')
                                datam={"name":t_music_n,"speaker":singer,"low":True}
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：0%"})
                                response1 = requests.post(url=song_url,data=json.dumps(datam),stream=True) 
                                for line in response1.iter_lines():
                                    decoded = (
                                        line.decode("unicode_escape")
                                        .replace("\b", "\\b")
                                        .replace("\f", "\\f")
                                        .replace("\r", "\\r")
                                        .replace("\t", "\\t")
                                        .replace("\n", "\\n")
                                    )
                                    done = json.loads(decoded)["done"]
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：{done}%"})
                                    if done == 100:
                                        file_name = json.loads(decoded)["name"]
                                        if "error:" in file_name:
                                            w_error = file_name.replace("error:","")
                                            if w_error == "time":
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，原因：歌曲过长"})
                                            else:
                                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习失败，错误码：%s"%w_error})
                                        else:
                                            with open("./data/voice/smusic/%s"%file_name, "wb") as f:
                                                response_wav = requests.get(url=f"{song_url}/output/{file_name}").content
                                                f.write(response_wav)
                                            # copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                            requests.post(url=f"{song_url}/removea/{file_name}",stream=True) 
                                            send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                            time.sleep(random.randrange(0,3))
                                            send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                    #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[未找到合适歌曲]"})
                            else:
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                            if random.randrange(0,80)==0:
                                # send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': random.choice(["呜呜，没有零花钱啦...","我亨阔耐，给我钱钱~","有没有好心人给点零花钱，求求啦！"])})
                                e_image_list=os.listdir(f"./data/image/{role}/money")
                                e_image=random.choice(e_image_list)
                                # send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%("money",e_image)})
                                send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%("money1","money.png")})
                            print(processed_d_data2)
                            print(user_chat_model)
                            objdict["banaijian%s"%rev['group_id']][0]=objdict["banaijian%s"%rev['group_id']][0]+[{'role':'user','content':temp_raw_msg},{'role':'assistant','content':processed_d_data2}]
                            with open(
                                f"./user/{role}/g{rev['group_id']}/memory.txt",
                                "a",
                                encoding="utf-8",
                            ) as txt:
                                timestamp = time.time()
                                localtime = time.localtime(timestamp)
                                current_time = time.strftime(
                                    "%Y-%m-%d %H:%M:%S", localtime
                                )
                                txt.write(
                                    "[%s]%s\n" % (current_time, temp_raw_msg)
                                )
                                txt.write(
                                    "[%s]你回复：%s\n"
                                    % (current_time, processed_d_data1)
                                )
                        
            print("未发现新消息...运行时间：%f"%(time.time()-startT))
            if "banaijian%s"%rev['group_id'] in objdict.keys() and len(objdict["banaijian%s"%rev['group_id']][0])> max_turn_group*16:
                objdict["banaijian%srecap"%rev['group_id']]=summarize_chat(objdict["banaijian%s"%rev['group_id']][0][:-max_turn_group*8],AI_name,think_url,think_model,think_key)
                objdict["banaijian%smem_i"%rev['group_id']].add_memory(objdict["banaijian%s"%rev['group_id']][0][:-max_turn_group*8])
                objdict["banaijian%s"%rev['group_id']][0]=[objdict["banaijian%s"%rev['group_id']][0][0]]+objdict["banaijian%s"%rev['group_id']][0][-max_turn_group*10:]

    except Exception as e:
        try:
            pass
            # objdict["banaijian%schat"%rev['group_id']]=''
        except Exception as ee:
            print(user_chat_model)
            print(ee)
        if debug:
            print(e)
            print(user_chat_model)
        pass






role = input("请输入要启动的角色名称：")





print("读取配置文件...")
with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    setinfo = setting.read()
    setdir = json.loads(setinfo)
    if role not in setdir["role"].keys():
        raise FileNotFoundError(f"{role}不存在！")
    draw_url = setdir["draw_url"]
    draw_key = setdir["draw_key"]
    draw_model = setdir["draw_model"]
    system_prompts = setdir["role"][role]["system_prompts"]
    chat_models = setdir["chat_models"]
    debug = setdir["role"][role]["debug"]
    triggers = setdir["role"][role]["triggers"]
    random_trigger = setdir["role"][role]["random_trigger"]
    AI_name = setdir["role"][role]["AI_name"]
    qq_id = setdir["role"][role]["qq_id"]
    ban_names = setdir["ban_names"]
    root_ids = setdir["role"][role]["root_ids"]
    send_debug = setdir["role"][role]["send_debug"]
    speaker = setdir["role"][role]["speaker"]
    is_voice = setdir["role"][role]["is_voice"]
    song = setdir["role"][role]["song"]
    singer = setdir["role"][role]["singer"]
    is_ban_set = setdir["role"][role]["is_ban_set"]
    max_turn_group=setdir["role"][role]["max_turn_group"]
    max_turn_private=setdir["role"][role]["max_turn_private"]
    send_port=setdir["role"][role]["send_port"]
    listen_port=setdir["role"][role]["listen_port"]
    see_url=setdir["see_url"]
    see_key=setdir["see_key"]
    see_model=setdir["see_model"]
    think_keywords=setdir["think_keywords"]
    enable_think=setdir["role"][role]["think"]
    tts_version=setdir["tts_version"]
    tts_url=setdir["tts_url"]
    song_url=setdir["song_url"]

think_url=chat_models[-1]["model_api"]
think_model=chat_models[-1]["model_name"]
think_key=chat_models[-1]["model_key"]

if tts_version == 2:
    is_tts_v2 = True
else:
    is_tts_v2 = False   

write_llbot_config(qq_id,send_port,listen_port)
import subprocess

# 直接运行 exe，使用 Popen 实现非阻塞，CREATE_NO_WINDOW 隐藏控制台窗口
subprocess.Popen(
    ["tools/llonebot/llbot.exe", "--qq", f"{qq_id}"]
)


ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(('127.0.0.1', listen_port))
ListenSocket.listen(100)

from flask import Flask, send_from_directory
from flask_cors import CORS
from waitress import serve
import os
import threading

app = Flask(__name__)
CORS(app)

@app.route('/data/image/<role>/<filename>', methods=['GET', 'POST'])
def image_files(role, filename):
    print(f"用户请求文件：{filename}，角色：{role}")
    base_dir = f'./data/image/{role}/'
    file_path = os.path.join(base_dir, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(base_dir, filename, as_attachment=True)
    else:
        return 'File not found', 404


@app.route('/data/voice/<filename>', methods=['GET', 'POST'])
def voice_files(filename):
    print("用户请求文件：", filename)
    if os.path.exists(os.path.join('./data/voice/', filename)):
        return send_from_directory('./data/voice/', filename, as_attachment=True)
    else:
        return 'File not found', 404

@app.route('/data/voice/smusic/<filename>', methods=['GET', 'POST'])
def music_files(filename):
    print("用户请求文件：", filename)
    if os.path.exists(os.path.join('./data/voice/smusic/', filename)):
        return send_from_directory('./data/voice/smusic/', filename, as_attachment=True)
    else:
        return 'File not found', 404
    
@app.route('/data/msface/<emotion>/<filename>', methods=['GET', 'POST'])
def msface_files(emotion,filename):
    print("用户请求文件：", emotion,"/",filename)
    if os.path.exists('./data/msface/%s/%s'%(emotion,filename)):
        return send_from_directory('./data/msface/%s'%emotion, filename, as_attachment=True)
    else:
        return 'File not found', 404
    
@app.route('/data/image/<role>/<emotion>/<filename>', methods=['GET', 'POST'])
def emoji_files(role, emotion, filename):
    print(f"用户请求文件：{filename}，角色：{role}，情绪：{emotion}")
    if os.path.exists(f"./data/image/{role}/{emotion}/{filename}"):
        return send_from_directory(f"./data/image/{role}/{emotion}", filename, as_attachment=True)
    else:
        return 'File not found', 404

# 定义一个函数来启动Flask应用
def run_server():
    serve(app, host='127.0.0.1', port=4321, threads=10)

# 创建并启动新线程
print("启用本地文件传输服务...")
thread = threading.Thread(target=run_server)
thread.start()

if not os.path.exists("./data/idname.json"):
    with open("./data/idname.json", 'w', encoding='utf-8') as f:
        json.dump({},f)
if not os.path.exists("./data/voice/smusic"):
    os.makedirs("./data/voice/smusic")
smusic_l=os.listdir("./data/voice/smusic")#载入本地音乐信息
str_music_l=""
for p_m_n in smusic_l:
    str_music_l += (p_m_n+",")

moodstr=''
for mood in system_prompts.keys():
    moodstr+=(mood+",")
moodstr=moodstr[:-1]

order = f"""

[order]
0. 每句话以及每个指令之间都必须使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split##split#幻日在不？#split# #split##pass/None##split#”
1. 需要经常查询记忆或回忆过去，必须按照格式 #split##searchmemory/检索关键词##split#，例如回忆幻日是什么专业相关记忆：#split##searchmemory/幻日 专业##split#（关键词尽量多，关键词之间用空格分隔）
2. 当需要发送表情包表达情绪时，按照格式 #split##emotion/情绪##split#，例如有人反复纠缠不休导致很生气：#split##emotion/angry##split#  (不要总是发送表情包，每条信息最多使用一次表情包，只支持以下表情包[angry,happy,sad,fear,bored])
3. 使用绘画功能时按照格式 #split##picture/draw prompt##split# ，例如绘画一个女孩： #split##picture/one girl##split#  （除非明确要求否则不要绘画；绘画提示词尽力充实丰富，细节饱满详细，提示词使用**英文**单词,English words）
4. 想生成原创歌曲时按照格式（较为常用） #split##makemusic/song name & song prompt & reference name & lyric##split#， 例如想原创一手悲伤的都市歌曲：#split##picture/多余的习惯& Slow urban ballad, acoustic guitar and soft piano, melancholic atmosphere, emotional male vocals, theme of heartbreak and lonely city night, sad mandopop style & 孤独患者 & (Verse 1)
走过那条熟悉的街角，风吹乱头发有些凌乱
路灯拉长孤单的身影，回想你最后说的晚安

(Chorus)
城市太大找不到出口，思念太重怎么去接收
说好的以后变成谎言，只剩下回忆赖着不走

(Verse 2)
便利店的灯光忽明忽暗，手里的咖啡早已变淡
看着人群匆匆忙忙聚散，明白孤单也是种习惯

(Chorus)
城市太大找不到出口，思念太重怎么去接收
说好的以后变成谎言，只剩下回忆赖着不走

(Bridge)
如果当时多一点挽留，是不是就不会放开手
可惜时光从来不回头，所有的假设都是借口

(Outro)
雨下整夜淋湿了以后，没人听见我的问候
故事结束在那个路口，只剩风在身后颤抖##split#  （参数分为四个，分别是起的歌名，生成音乐的提示词，最符合提示词的参考音乐的名称和音乐的歌词，四部分使用“&”分开，且四部分的内容不可出现“&”；提示词尽可能具体，包含风格与流派、情绪与氛围、速度与节奏等；歌词需要分块并使用(Verse) / (Pre-Chorus) / (Chorus) / (Bridge) / (Outro)等类似标签并做到每一句歌词工整对仗有押韵，歌词不要太短，不要加入任何特殊标点符号，生成纯音乐时歌词内容为(instrument)）
4. 需要联网搜索互联网信息时按照格式 #split##searchweb/搜索关键词##split#，例如查询国内的新闻：#split##searchweb/国内 新闻 信息##split#  （关键词尽量多，详细，具体，允许经常使用）
5. 每隔一段时间有重要的信息点需要写入长期记忆 #split##memory/写入的信息内容##split#，例如提到幻日是大学生开发者：#split##memory/幻日是大学生开发者##split# （信息尽可能精简，不要写入有时效性的类似“明天是周天”的信息会失效造成干扰，不要写入[self_impression]下已经存在的内容）
6. 不想或者不需要回复信息时，只需要输出 #split##pass/None##split#，例如提到的信息与你无关-“@蓝莓 你是坏蛋”： #split##pass/None##split# (不要总是使用此操作拒绝回复)
7. 需要切换自身心情时，按照格式 #split##mood/心情名##split#，例如有人惹你生气：#split##mood/angry##split#，心情平复后：#split##mood/default##split#（非必要不要情感，只支持以下心情[{moodstr}]）
8. 需要戳戳其他人，按照格式 #split##poke/要戳的对方的qq号（不是名称）##split#，例如有人不断戳你，他的qq号是123456789，你也想戳他：#split##poke/123456789##split#
9. 需要执行任何上述指令无法实现的操作，按照格式 #split##do/需要做的事情##split#，例如需要找幻日的开发日志：#split##do/在电脑内搜索幻日的开发日志 日志名称可能带有的关键字包括 幻日 log 日志 开发 然后输出文件路径##split#   (较为常用，任何除上述指令外的操作都需要使用此do指令，使用时尽可能叙述操作执行的要求和详细步骤)
10.不要使用括号配合神情，动作描写，也不要理会使用括号表达动作的人例如“群友：（抱了抱你）”，你应该pass
"""
if is_voice:
    if is_tts_v2:
        order+="""
10. 使用语音时按照格式 #split##voice/[情感向量]语言合成的内容##split# ，其中情绪向量由["喜", "怒", "哀", "惧", "厌恶", "低落", "惊喜", "平静"]按顺序构成，例如在开心时语音输出“你好丫”： #split##voice/[0.55, 0, 0, 0, 0, 0, 0.1, 0]你好丫##split#  (不要过多使用语音；使用语音时不可使用（括号）和特殊字符)"""
    else:
        order+="""
10. 使用语音时按照格式 #split##voice/语言合成的内容##split# ，例如语音输出“你好”： #split##voice/你好##split#  (不要过多使用语音；使用语音时不可使用（括号）和特色字符)"""
if song:
    order+="""
11. 心情好或想要唱歌时，按照格式 #split##music/歌曲名##split#，例如有人想让你唱潮汐：#split##music/潮汐##split# (不要总是唱歌) **注意与makemusic行为区分，makemusic是创作原创音乐，music是执行翻唱行为**"""
if is_ban_set:
    order+="""
12.被人骚扰时，可尝试将对方禁言，按照格式 #split##ban/要禁言的QQ号(不是名称)-禁言时长(分钟)##split#，例如有人对你说不雅之语，想禁言五分钟，他的QQ号"qq:123456789"：#split##ban/123456789-5##split#（不要经常禁言其他人，禁言要关注并确定输入正确的qq号和应得的禁言时长；注意：如果要解除禁言，只需要将禁言时长改为0，其他格式不变即可）
    """
order+="""
回复时，禁止以群友的名义重复或冒充群友说话，并且注意：这是在群聊而非任何现实场景，不要使用动作描述，如果有人用现实动作描述与你对话，请反驳他


接下来每次对话会提供以下内容：
1.<think>回复参考提示</think>段内容供你参考（此内容可供参考和提供回复灵感，具体回复内容可以自由发挥）
2.<qq>来自qq的信息</qq>（请主要回复此内容，不可提及你的设定及以上用于规范化的信息以及其他无关内容）
"""



"""
[question]有人问桌宠或qbot相关问题时可以参考下列常见问题和帮助回答
1.闪退：在软件文件夹下进入通过cmd运行程序即可看到报错并反馈给幻日
2.切换角色：在桌宠文件夹下打开一键资源下载器，选择一键切换角色
3.桌宠连不上服务器：尝试重启或叫幻日检查服务器网络
4.桌宠不说话或本地语音合成出错：检查本地语音合成终端报错信息并联系幻日老爹，只支持v1版本语音模型，设置路径为纯英文，最新版自带本地语音合成不用下载
5.qbot后台没反应：检查qq的llonebot插件配置，特别是上报地址是否填好为http:127.0.0.1:3001
6.qbot收到消息但是没回复：可能是模型问题，可尝试去智谱清言官方网站找免费模型glm-4-flash，注意填写正确的请求api，key以及模型名称
"""#在这里可以添加一些想让AI高权重知道的一些信息等，不宜太多

system_prompt=system_prompts["default"]
system= system_prompt+order

for mood in system_prompts.keys():
    system_prompts[mood]+=order

ttsurls=tts_url
ttsurls_v2=tts_url
jieyue=True
cpu_lacking=False    
weihu=False#是否暂停qq机器人进入维护状态
remove_kuohao=False
is_filt=True

filted_words=["TM","丫的","SB","神金","sb","傻逼"]

objdict={}
ban_id_dir={}
processed_d_data='想聊天'
startT=time.time()#总计时开始
print('程序已启动')

while 1:
    try:
        

        def is_sleep_time():
            # 获取当前时间的时、分
            now = time.localtime()
            current_hour = now.tm_hour
            current_min = now.tm_min
            
            # 将当前时间转换为“当天过了多少分钟”
            # 例如：23:50 -> 23*60 + 50 = 1430
            # 例如：07:00 -> 7*60 + 0 = 420
            current_total_mins = current_hour * 60 + current_min
            
            # 定义睡眠起止时间（转换成分钟数）
            start_mins = 23 * 60 + 30  # 23:50 -> 1430
            end_mins = 7 * 60 + 50          # 07:00 -> 420
            
            # 判断逻辑：
            # 正常时间段是 start < end，但跨天的时间段是 start > end
            # 如果当前分钟数 >= 晚上23:50 (1430)，或者 <= 早上7:00 (420)，则为睡眠时间
            if current_total_mins >= start_mins or current_total_mins <= end_mins:
                return True
            else:
                return False

        # 测试
        if is_sleep_time():
            weihu = True
        else:
            weihu = False

        rev = rev_msg()
        try:
            botID=rev['self_id']
        except:
            pass
        try:
            msface_summary = rev["message"][0]["data"]["summary"].replace("[","").replace("]","")
            if len(msface_data)>1:
                msface_url = rev["message"][0]["data"]["url"]
                msface_data = requests.get(msface_url)
                if not os.path.exists(f"./data/msface/{msface_summary}"):
                    os.makedirs(f"./data/msface/{msface_summary}")
                msface_list = os.listdir(f"./data/msface/{msface_summary}")
                with open(f"./data/msface/{msface_summary}/{len(msface_list)}.gif","wb") as f:
                    f.write(msface_data.content)
        except:
            pass
        if rev == None:
            continue
    except:
        continue
    Thread(target=main,args=(rev,)).start()


