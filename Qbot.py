print('\n欢迎使用由幻日编写的幻蓝AI-Qbot1.1程序，有疑问请联系q：2141073363')
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import time
import random
import requests
import json
import os
from receive import rev_msg
import socket
import re
from threading import Thread
import base64
import jieba.analyse
from bs4 import BeautifulSoup

def change_setting(file_name,key,value):
    with open(file_name, 'r', encoding='utf-8') as f:
        t_gsetting=json.load(f)
    t_gsetting[key]=value
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(t_gsetting, f, ensure_ascii=False, indent=4)


def search(query):
    """
    Searches the web for the specified query and returns the results.
    """
    response = requests.get(
        'https://api.openinterpreter.com/v0/browser/search',
        params={"query": query},
    )
    if response.status_code==200 and response.json()["result"]:
        return response.json()["result"]
    else:
        querys=query.split(" ")
        result = bing_search(querys)
        if result:
            return result
        else:
            result = bing_search(query)
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
            if current_role == "user":
                current_content = "[特殊消息]"
            else:
                current_content = "呜呜，遇到未知错误..."

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
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return "\n[self_impression]\n"+content[-400:]

def get_memory(file_path, keywords, match_n=200, time_n=200, radius=50):
    """
    读取整个文件，搜索关键词，合并重叠文段，并返回两个排序的文段列表：
    1. 包含关键词个数排名前五的文段。
    2. 越靠近文段末尾的排在前面，同样返回五个，且不与第一个列表重复。

    :param file_path: 文件路径
    :param keywords: 关键词列表
    :param radius: 关键词附近要返回的文本字数
    :return: 关键词匹配记忆
    """
    # 读取整个文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

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
        if "cogview" in draw_model:
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
        response=requests.post(url=urldraw,headers=headers,stream=True,data=json.dumps(data))
        if response.status_code==200:
            send_msg({'msg_type': 'group', 'number': to, 'msg': '绘画完毕发送中...'})
        processed_d_data_draw=''
        for line in response.iter_lines():
            try:
                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                if decoded != '':
                    if "cogview" in draw_model:
                        processed_d_data_draw+=json.loads(decoded)["data"][0]["url"]
                    else:
                        processed_d_data_draw+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]

                    print(decoded)
            except Exception as e:
                print(e)
        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
        print(image_url)
        max_n=500
        for n in range(0,max_n):
            try:
                image_response=requests.get(image_url)
                name=str(random.randrange(100000,999999))+'.png'
                with open("./data/image/%s"%name,'wb') as f_image:
                    f_image.write(image_response.content)
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
        
        if "cogview" in draw_model:
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
        response=requests.post(url=urldraw,headers=headers,stream=True,data=json.dumps(data))
        if response.status_code==200:
            send_msg({'msg_type': 'private', 'number': to, 'msg': '绘画完毕发送中...'})
        processed_d_data_draw=''
        for line in response.iter_lines():
            try:
                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                if decoded != '':
                    if "cogview" in draw_model:
                        processed_d_data_draw+=json.loads(decoded)["data"][0]["url"]
                    else:
                        processed_d_data_draw+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                    print(decoded)
            except Exception as e:
                print(e)
        image_url=processed_d_data_draw.split('(')[-1].replace(')','')
        print(image_url)
        max_n=500
        for n in range(0,max_n):
            try:
                image_response=requests.get(image_url)
                name=str(random.randrange(100000,999999))+'.png'
                with open("./data/image/%s"%name,'wb') as f_image:
                    f_image.write(image_response.content)
                send_image({'msg_type': 'private', 'number': to, 'msg':name })
                break
            except:
                print(n)
                if n==max_n-1:
                    raise TimeoutError("重试无效")
    except Exception as e:
        print('绘画错误:',e)
        send_msg({'msg_type': 'private', 'number': to, 'msg':'AI绘画操作无法执行'})
        
def send_msg(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg'].strip()  # 要回复的消息
    if msg:
        if msg_type == 'group':
            res=requests.post('http://localhost:3000/send_group_msg', json={
                'group_id': number,
                'message': msg
            })
            print("send_group_msg:",msg,json.loads(res.content))
        elif msg_type == 'private':
            res=requests.post('http://localhost:3000/send_private_msg', json={
                'user_id': number,
                'message': msg
            })
            print("send_private_msg:",msg,json.loads(res.content))
    return 0

def send_image(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post('http://localhost:3000/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:image,file=http://127.0.0.1:4321/data/image/%s]"%msg
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post('http://localhost:3000/send_private_msg', json={
            'user_id': number,
            'message':"[CQ:image,file=http://127.0.0.1:4321/data/image/%s]"%msg
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_voice(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post('http://localhost:3000/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:record,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post('http://localhost:3000/send_private_msg', json={
            'user_id': number,
            'message':"[CQ:record,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_music(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post('http://localhost:3000/send_group_msg', json={
            'group_id': number,
            'message': "[CQ:file,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_group_msg:",msg,json.loads(res.content))
    elif msg_type == 'private':
        res=requests.post('http://localhost:3000/send_private_msg', json={
            'user_id': number,
            'message':"[CQ:file,file=http://127.0.0.1:4321/data/voice/%s]"%msg
        })
        print("send_private_msg:",msg,json.loads(res.content))

def send_image_url(resp_dict):
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    if msg_type == 'group':
        res=requests.post('http://localhost:3000/send_group_msg', json={
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
        res=requests.post('http://localhost:3000/send_private_msg', json={
            'user_id': number,
            'message': {
                        "type": "image",
                        "data": {
                            "file": "%s"%msg
                        }
                    }
        })
        print("send_private_msg:",msg,json.loads(res.content))       

def choose_model():
    w_c_models=[]
    for c_model in chat_models:
        w_c_models+=[c_model]*c_model["weight"]
    model_info = random.choice(w_c_models)
    return model_info["model_api"],model_info["model_name"],model_info["model_key"]

def main(rev):
    global objdict
    user_api,user_chat_model,user_key=choose_model()
    try:
        timestamp = time.time()
        localtime = time.localtime(timestamp)
        current_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", localtime
            )
        e_information="[information](准确 有时效性)\n当前时间：%s\n"%current_time
        if rev["message_type"] == "private":
            if "banaijian%schat"%rev["sender"]["user_id"] not in objdict.keys():
                objdict["banaijian%schat"%rev["sender"]["user_id"]]=""
            if not os.path.exists("./user/p%s"%rev["sender"]["user_id"]):
                os.makedirs("./user/p%s"%rev["sender"]["user_id"])
                with open("./user/p%s/memory.txt"%rev["sender"]["user_id"],"w") as tpass:
                    pass
            if not os.path.exists("./user/p%s/I_memory.txt"%rev["sender"]["user_id"]):
                with open("./user/p%s/I_memory.txt"%rev["sender"]["user_id"],"w") as tpass:
                    pass
            
            if "[CQ:image,"  not in rev['raw_message']:
                objdict["banaijian%schat"%rev["sender"]["user_id"]]+=(rev["sender"]["nickname"]+"："+rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')+'\n\n')
                objdict["banaijian%schat"%rev["sender"]["user_id"]]=objdict["banaijian%schat"%rev["sender"]["user_id"]][-50:]

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
                    if weihu:
                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "维护中..."})
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
                    s_memory=get_memory("./user/p%s/memory.txt"%rev["sender"]["user_id"],keywords)
                    s_memory+=get_I_memory("./user/p%s/I_memory.txt"%rev["sender"]["user_id"])
                    print(s_memory)
                    data={
                            "model": user_chat_model,##claude-3-opus-vf
                            "messages":merge_contents([{"role":"system","content":messages[0]["content"]+"[memory](模糊 无时效性)\n%s\n"%s_memory+e_information}]+messages[1:]),
                            "stream": True,
                            "use_search": False
                        }
                    is_return=True
                    while is_return:
                        is_return=False
                        for _ in range(0,3):
                            try:
                                response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                                if response.status_code==200:
                                    break
                                print("请求错误，尝试兜底模型")
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                            except Exception as e:
                                print("请求错误，尝试兜底模型：",e)
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                        temp_tts_list=[]
                        processed_d_data1=''
                        for line in response.iter_lines():
                            try:
                                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                                if decoded != '':
                                    processed_d_data1+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                            except Exception as e:
                                continue
                                pass
                            lastlen=len(temp_tts_list)
                            temp_tts_list=processed_d_data1.split("#split#")
                            if not temp_tts_list:
                                temp_tts_list=temp_tts_list[:-1]
                            if self_id not in objdict["banaijian%sgeneing"%rev["sender"]["user_id"]]:
                                objdict["banaijian%s"%rev["sender"]["user_id"]][0]=objdict["banaijian%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                                raise InterruptedError("新消息中断")
                            
                            if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                                if '#voice/' in temp_tts_list[-2]:
                                    try:
                                        voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                        tts_data = {
                                        "cha_name": "illue",#这里填本地语音合成包里面配置好的说话人
                                        "text": voice.replace("...", "…").replace("…", ","),
                                        "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                        }
                                        b_wav = requests.post(
                                            url='http://127.0.0.1:5000/tts', json=tts_data
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
                                elif '#picture/' in temp_tts_list[-2]:
                                    picture=temp_tts_list[-2].split('#picture/')[-1].replace("#",'')
                                    print(picture)
                                    draw_private(picture,rev["sender"]["user_id"])
                                elif '#search/' in temp_tts_list[-2]:
                                        response.close()
                                        temp_tts_list=temp_tts_list[:-1]
                                        break   
                                elif '#memory/' in temp_tts_list[-2]:
                                    memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                    print("写入记忆：",memory)    
                                    with open("./user/p%s/I_memory.txt"%rev["sender"]["user_id"],"a",encoding="utf-8") as mem:
                                        mem.write(" "+memory) 
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[写入记忆]"})
                                elif "#pass/" in temp_tts_list[-2]:
                                    response.close()
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[pass]"})
                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                elif "#emotion/" in temp_tts_list[-2]:
                                    t_emotion=temp_tts_list[-2].split("#emotion/")[-1].replace("#",'')
                                    e_image_list=os.listdir("./data/image/%s"%t_emotion)
                                    e_image=random.choice(e_image_list)
                                    send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%(t_emotion,e_image)})
                                elif "#music/" in temp_tts_list[-2]:
                                    t_music_n=temp_tts_list[-2].split("#music/")[-1].replace("#",'')
                                    smusic_l=os.listdir("./data/voice/smusic")
                                    if t_music_n in smusic_l:
                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%t_music_n})
                                        send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+t_music_n})
                                    else:
                                        send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                                else:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-2].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                        if "抱歉" in temp_tts_list[-1]:
                            objdict["banaijian%s"%rev["sender"]["user_id"]][0]=[objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]]
                            print("催眠失败，重置记忆")
                        else:
                            if '#voice/' in temp_tts_list[-1]:
                                voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                                tts_data = {
                                    "cha_name": "illue",#这里填本地语音合成包里面配置好的说话人
                                    "text": voice.replace("...", "…").replace("…", ","),
                                    "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                    }
                                b_wav = requests.post(
                                    url='http://127.0.0.1:5000/tts', json=tts_data
                                    )
                                n=random.randrange(10000,99999)
                                name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                to_path='./data/voice/%s'%name
                                with open(to_path,'wb') as wbf:
                                    wbf.write(b_wav.content)
                                send_voice({'msg_type': 'private', 'number':rev["sender"]["user_id"], 'msg':name })
                            elif '#picture/' in temp_tts_list[-1]:
                                picture=temp_tts_list[-1].split('#picture/')[-1].replace("#",'')
                                print(picture)
                                draw_private(picture,rev["sender"]["user_id"])
                            elif '#search/' in temp_tts_list[-1]:
                                
                                s_prompt=temp_tts_list[-1].split('#search/')[-1].replace("#",'')
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "正在联网搜索：%s"%s_prompt})
                                search_result=search(s_prompt)
                                print(search_result)
                                objdict["banaijian%s"%rev["sender"]["user_id"]][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1+"""\nsystem[搜索结果不可见]：正在联网搜索：%s\n搜索结果：\n%s\n由于system返回的搜索结果你应该看不见，我将用自己的话详细，具体的讲述一下搜索结果。"""%(s_prompt,search_result)},{"role":"user","content":"开始详细具体的讲述吧"}]
                                messages=objdict["banaijian%s"%rev["sender"]["user_id"]][0]
                                data={
                                    "model": user_chat_model,##claude-3-opus-vf
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日老爹在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False
                                }
                                is_return=True
                                continue
                            elif '#memory/' in temp_tts_list[-1]:
                                memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                print("写入记忆：",memory)    
                                with open("./user/p%s/I_memory.txt"%rev["sender"]["user_id"],"a",encoding="utf-8") as mem:
                                    mem.write(" "+memory) 
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[写入记忆]"})
                            elif "#pass/" in temp_tts_list[-1]:
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[pass]"})
                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                            elif "#emotion/" in temp_tts_list[-1]:
                                t_emotion=temp_tts_list[-1].split("#emotion/")[-1].replace("#",'')
                                e_image_list=os.listdir("./data/image/%s"%t_emotion)
                                e_image=random.choice(e_image_list)
                                send_image({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"%s/%s"%(t_emotion,e_image)})
                            elif "#music/" in temp_tts_list[-1]:
                                t_music_n=temp_tts_list[-1].split("#music/")[-1].replace("#",'')
                                smusic_l=os.listdir("./data/voice/smusic")
                                if t_music_n in smusic_l:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "《%s》"%t_music_n})
                                    send_voice({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg':"smusic/"+t_music_n})
                                else:
                                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': "[未找到合适歌曲]"})
                            else:
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-1].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                            print(processed_d_data1)
                            objdict["banaijian%s"%rev["sender"]["user_id"]][0]=objdict["banaijian%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                            with open(
                                    "./user/p%s/memory.txt"%rev["sender"]["user_id"],
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
            if len(objdict["banaijian%s"%rev["sender"]["user_id"]][0])> 10:
                objdict["banaijian%s"%rev["sender"]["user_id"]][0]=[objdict["banaijian%s"%rev["sender"]["user_id"]][0][0]]+objdict["banaijian%s"%rev["sender"]["user_id"]][0][-6:]  
            objdict["banaijian%schat"%rev["sender"]["user_id"]]=''
            

        elif rev["message_type"] == "group":
            if ("团子" in rev["sender"]["nickname"] or "芙芙" in rev["sender"]["nickname"] or "炼丹师" in rev["sender"]["nickname"]) and "[CQ:image," in rev['raw_message']:
                time.sleep(5+random.randrange(0,5))
                message_id=rev['message_id']
                res=requests.post('http://localhost:3000/delete_msg', json={
                    'message_id': message_id,
                })
                print("delete_msg:",rev['raw_message'],json.loads(res.content))

            pass_ban=False
            for ban_name in ban_names:
                if ban_name in rev["sender"]["nickname"]:
                    pass_ban = True
                    break
            if pass_ban:
                raise RuntimeError("break limitless turn")#屏蔽指定名称qq
            

            if "banaijian%schat"%rev['group_id'] not in objdict.keys():#创建目录
                objdict["banaijian%schat"%rev['group_id']]=""
            if not os.path.exists("./user/g%s"%rev['group_id']):
                os.makedirs("./user/g%s"%rev['group_id'])
                with open("./user/g%s/memory.txt"%rev['group_id'],"w") as tpass:
                    pass
            if not os.path.exists("./user/g%s/I_memory.txt"%rev['group_id']):
                with open("./user/g%s/I_memory.txt"%rev['group_id'],"w") as tpass:
                    pass
            if not os.path.exists("./user/g%s/setting.json"%rev['group_id']):
                data={'mood':'default','random_trigger':random_trigger,"root_id":root_ids}
                with open("./user/g%s/setting.json"%rev['group_id'], 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

            
            if "[CQ:image,"  not in rev['raw_message']:#组建单次回复上下文
                objdict["banaijian%schat"%rev['group_id']]=objdict["banaijian%schat"%rev['group_id']][-50:]
                objdict["banaijian%schat"%rev['group_id']]+=(rev["sender"]["nickname"]+"："+rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')+'\n\n')
                
            if "#settitle:" in rev['raw_message']:#自动设置头衔（暂时无效）
                title=rev['raw_message'].split(':',1)[-1][:5]
                res=requests.post('http://localhost:3000/set_group_special_title', json={
                    'group_id': rev['group_id'],
                    'user_id': rev['user_id'],
                    'special_title':title,
                    'duration':-1
                })
                print("set_group_special_title:",rev['raw_message'].split(':',1)[-1][:5],json.loads(res.content))
            with open("./user/g%s/setting.json"%rev['group_id'], 'r', encoding='utf-8') as f:
                tt_gsetting=json.load(f)
            tt_random_trigger=tt_gsetting["random_trigger"]
            is_trigger=False#比对触发词
            for trigger in triggers:
                if trigger in rev['raw_message']:
                    is_trigger = True
                    break
            if (is_trigger or '[CQ:at,qq=%d]'%rev['self_id'] in rev['raw_message'] or random.randrange(0,tt_random_trigger)==0):#触发回复
                a=objdict["banaijian%schat"%rev['group_id']]
                print(a)
                self_id=random.randrange(100000,999999)
                objdict["banaijian%sgeneing"%rev['group_id']]=[self_id] 
                rev['raw_message']=rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')
                if "banaijian%s"%rev['group_id'] not in objdict.keys():
                    objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                if '#reset' in rev['raw_message']:
                    objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '已清空对话历史'}) 
                elif "#mood" in rev['raw_message'] and rev['user_id'] in root_ids:
                    for tt_mood in system_prompts.keys():
                        if tt_mood in rev['raw_message'].replace("#mood",""):
                            objdict["banaijian%s"%rev['group_id']]=[[{'role':'system','content':system_prompts[tt_mood]}]]
                            change_setting("./user/g%s/setting.json"%rev['group_id'],"mood",tt_mood)
                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[%s]'%tt_mood}) 
                            break
                elif "#random" in rev['raw_message'] and rev['user_id'] in root_ids:
                    t_random_trigger=int(rev['raw_message'].split(" ")[-1])
                    change_setting("./user/g%s/setting.json"%rev['group_id'],"random_trigger",t_random_trigger)
                    if t_random_trigger<=0:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[已关机]'}) 
                    else:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '[触发率设置为1/%d]'%t_random_trigger}) 
                    
                else:        
                    if tt_random_trigger < 1:
                        raise KeyboardInterrupt("群聊已停止回复")
                    processed_d_data="强制切换意图"
                    turl=user_api
                    if random.randrange(0,10)==0:#在这里切换情感复原的概率
                        objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts["default"]}
                    if weihu:
                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[维护中...]"})
                        raise KeyboardInterrupt("维护ing")
                    print(processed_d_data)
                    if not processed_d_data:
                        processed_d_data='.'
                    turl=user_api
                    headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer "+user_key
                        }
                    messages=objdict["banaijian%s"%rev['group_id']][0]+[{"role":"user","content":objdict["banaijian%schat"%rev['group_id']]}]
                    keywords = jieba.analyse.extract_tags(rev['raw_message'].replace(AI_name,""), topK=50)
                    s_memory=get_memory("./user/g%s/memory.txt"%rev['group_id'],keywords,match_n=500)
                    s_memory+=get_I_memory("./user/g%s/I_memory.txt"%rev['group_id'])
                    print(s_memory)
                    data={
                            "model": user_chat_model,
                            "messages":merge_contents([{"role":"system","content":messages[0]["content"]+"[memory](模糊 无时效性)\n%s\n"%s_memory+e_information}]+messages[1:]),
                            "stream": True
                        }
                    is_return=True
                    while is_return:
                        is_return=False
                        for _ in range(0,3):
                            try:
                                response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                                if response.status_code==200:
                                    break
                                print("请求错误，尝试兜底模型")
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                            except Exception as e:
                                print("请求错误，尝试兜底模型：",e)
                                data["model"]=chat_models[0]["model_name"]
                                turl=chat_models[0]["model_api"]
                                user_key=chat_models[0]["model_key"]
                                headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Bearer "+user_key
                                }
                        temp_tts_list=[]
                        processed_d_data1=''
                        for line in response.iter_lines():
                            try:
                                decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                                if decoded != '':
                                    processed_d_data1+=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                            except Exception as e:
                                print(decoded,e)
                                continue
                                pass
                            lastlen=len(temp_tts_list)
                            temp_tts_list=processed_d_data1.split("#split#")
                            if not temp_tts_list:
                                temp_tts_list=temp_tts_list[:-1]
                            if self_id not in objdict["banaijian%sgeneing"%rev['group_id']]:
                                objdict["banaijian%s"%rev['group_id']][0]=objdict["banaijian%s"%rev['group_id']][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                                raise InterruptedError("新消息中断")
                            
                            if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                                if '#voice/' in temp_tts_list[-2]:
                                    try:
                                        voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                        tts_data = {
                                        "cha_name": "illue",#这里填本地语音合成包里面配置好的说话人
                                        "text": voice.replace("...", "…").replace("…", ","),
                                        "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                        }
                                        b_wav = requests.post(
                                            url='http://127.0.0.1:5000/tts', json=tts_data
                                            )
                                        n=random.randrange(10000,99999)
                                        name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                        to_path='./data/voice/%s'%name
                                        with open(to_path,'wb') as wbf:
                                            wbf.write(b_wav.content)
                                        send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':name })
                                    except Exception as e:
                                        print("暂不支持语音合成")
                                elif '#picture/' in temp_tts_list[-2]:
                                    picture=temp_tts_list[-2].split('#picture/')[-1].replace("#",'')
                                    print(picture)
                                    draw_group(picture,rev['group_id'])
                                elif '#search/' in temp_tts_list[-2]:
                                    response.close()
                                    temp_tts_list=temp_tts_list[:-1]
                                    break
                                elif '#memory/' in temp_tts_list[-2]:
                                    memory=temp_tts_list[-2].split('#memory/')[-1].replace("#",'')
                                    print("写入记忆：",memory)    
                                    with open("./user/g%s/I_memory.txt"%rev['group_id'],"a",encoding="utf-8") as mem:
                                        mem.write(" "+memory)
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[写入记忆]"})
                                elif "#pass/" in temp_tts_list[-2]:
                                    response.close()
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[pass]"})
                                    raise KeyboardInterrupt("AI认为应该跳过此回复！")
                                elif "#emotion/" in temp_tts_list[-2]:
                                    t_emotion=temp_tts_list[-2].split("#emotion/")[-1].replace("#",'')
                                    e_image_list=os.listdir("./data/image/%s"%t_emotion)
                                    e_image=random.choice(e_image_list)
                                    send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%(t_emotion,e_image)})
                                elif "#mood/" in temp_tts_list[-2]:
                                    t_mood=temp_tts_list[-2].split("#mood/")[-1].replace("#",'')
                                    try:
                                        objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts[t_mood]}
                                        change_setting("./user/g%s/setting.json"%rev['group_id'],"mood",t_mood)
                                        send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[%s]"%t_mood})
                                    except Exception as e:
                                        print("切换情感错误：",e)
                                elif "#music/" in temp_tts_list[-2]:
                                    t_music_n=temp_tts_list[-2].split("#music/")[-1].replace("#",'')
                                    
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：0%"})
                                    datam={"name":t_music_n,"speaker":"illue","low":True}
                                    response1 = requests.post(url="http://127.0.0.1:3333",data=json.dumps(datam),stream=True)
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
                                                    response_wav = requests.get(url="http://127.0.0.1:3333/output/%s"%file_name, timeout=60).content
                                                    f.write(response_wav)
                                                #copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                                requests.post(url="http://127.0.0.1:3333/removea/%s"%file_name,stream=True) 
                                                send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                                time.sleep(random.randrange(0,3))
                                                send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                        #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[未找到合适歌曲]"})
                                else:
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-2].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                        if "抱歉" in temp_tts_list[-1]:
                            objdict["banaijian%s"%rev['group_id']][0]=[objdict["banaijian%s"%rev['group_id']][0][0]]
                            print("催眠失败，重置记忆")
                        else:
                            if '#voice/' in temp_tts_list[-1]:
                                voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                                tts_data = {
                                    "cha_name": "illue",#这里填本地语音合成包里面配置好的说话人
                                    "text": voice.replace("...", "…").replace("…", ","),
                                    "character_emotion":random.choice(['default','angry','excited','narration-relaxed','depressed'])
                                    }
                                b_wav = requests.post(
                                    url='http://127.0.0.1:5000/tts', json=tts_data
                                    )
                                n=random.randrange(10000,99999)
                                name='%stts%d.wav'%((time.strftime('%F')+'-'+time.strftime('%T').replace(':','-')),n)
                                to_path='./data/voice/%s'%name
                                with open(to_path,'wb') as wbf:
                                    wbf.write(b_wav.content)
                                send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':name })
                            elif '#picture/' in temp_tts_list[-1]:
                                picture=temp_tts_list[-1].split('#picture/')[-1].replace("#",'')
                                print(picture)
                                draw_group(picture,rev['group_id'])
                            elif '#search/' in temp_tts_list[-1]:

                                s_prompt=temp_tts_list[-1].split('#search/')[-1].replace("#",'')
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "正在联网搜索：%s"%s_prompt})
                                search_result=search(s_prompt)
                                print(search_result)
                                objdict["banaijian%s"%rev['group_id']][0]+=[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1+"""\nsystem[搜索结果不可见]：正在联网搜索：%s\n搜索结果：\n%s\n由于system返回的搜索结果你应该看不见，我将用自己的话详细，具体的讲述一下搜索结果。"""%(s_prompt,search_result)},{"role":"user","content":"开始详细具体的讲述吧"}]
                                messages=objdict["banaijian%s"%rev['group_id']][0]
                                data={
                                    "model": user_chat_model,
                                    "messages":merge_contents([{"role":"system","content":system_prompt+"[order]\n1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日老爹在不？#split#”\n"+e_information}]+messages[1:]),
                                    "stream": True,
                                    "use_search": False
                                }
                                is_return=True
                                continue
                            elif '#memory/' in temp_tts_list[-1]:
                                memory=temp_tts_list[-1].split('#memory/')[-1].replace("#",'')
                                print("写入记忆：",memory)    
                                with open("./user/g%s/I_memory.txt"%rev['group_id'],"a",encoding="utf-8") as mem:
                                    mem.write(" "+memory)
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[写入记忆]"})
                            elif "#pass/" in temp_tts_list[-1]:
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[pass]"})
                                raise KeyboardInterrupt("AI认为应该跳过此回复！")
                            elif "#emotion/" in temp_tts_list[-1]:
                                t_emotion=temp_tts_list[-1].split("#emotion/")[-1].replace("#",'')
                                e_image_list=os.listdir("./data/image/%s"%t_emotion)
                                e_image=random.choice(e_image_list)
                                send_image({'msg_type': 'group', 'number': rev['group_id'], 'msg':"%s/%s"%(t_emotion,e_image)})
                            elif "#mood/" in temp_tts_list[-1]:
                                t_mood=temp_tts_list[-1].split("#mood/")[-1].replace("#",'')
                                try:
                                    objdict["banaijian%s"%rev['group_id']][0][0]={"role":"system","content":system_prompts[t_mood]}
                                    change_setting("./user/g%s/setting.json"%rev['group_id'],"mood",t_mood)
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[%s]"%t_mood})
                                except Exception as e:
                                    print("切换情感错误：",e)
                            elif "#music/" in temp_tts_list[-1]:
                                t_music_n=temp_tts_list[-1].split("#music/")[-1].replace("#",'')
                                datam={"name":t_music_n,"speaker":"illue","low":True}
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': f"歌曲《{t_music_n}》学习进度：0%"})
                                response1 = requests.post(url="http://127.0.0.1:3333",data=json.dumps(datam),stream=True) 
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
                                                response_wav = requests.get(url="http://127.0.0.1:3333/output/%s"%file_name, timeout=60).content
                                                f.write(response_wav)
                                            # copy_file("D:\\program-illusion\\realtime-song\\output\\%s"%file_name,"./data/voice/smusic")
                                            requests.post(url="http://127.0.0.1:3333/removea/%s"%file_name,stream=True) 
                                            send_voice({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                            time.sleep(random.randrange(0,3))
                                            send_music({'msg_type': 'group', 'number': rev['group_id'], 'msg':"smusic/"+file_name})
                                    #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "[未找到合适歌曲]"})
                            else:
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("%s："%AI_name,"").replace("%s:"%AI_name,"")})
                            print(processed_d_data1)
                            print(user_chat_model)
                            objdict["banaijian%s"%rev['group_id']][0]=objdict["banaijian%s"%rev['group_id']][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                            with open(
                                "./user/g%s/memory.txt"%rev['group_id'],
                                "a",
                                encoding="utf-8",
                            ) as txt:
                                timestamp = time.time()
                                localtime = time.localtime(timestamp)
                                current_time = time.strftime(
                                    "%Y-%m-%d %H:%M:%S", localtime
                                )
                                txt.write(
                                    "[%s]%s\n" % (current_time, objdict["banaijian%schat"%rev['group_id']])
                                )
                                txt.write(
                                    "[%s]你回复：%s\n"
                                    % (current_time, processed_d_data1)
                                )
                        objdict["banaijian%schat"%rev['group_id']]=''
            print("未发现新消息...运行时间：%f"%(time.time()-startT))
            if len(objdict["banaijian%s"%rev['group_id']][0])> 18:
                objdict["banaijian%s"%rev['group_id']][0]=[objdict["banaijian%s"%rev['group_id']][0][0]]+objdict["banaijian%s"%rev['group_id']][0][-6:]
    except Exception as e:
        try:
            objdict["banaijian%schat"%rev['group_id']]=''
        except Exception as ee:
            print(user_chat_model)
            print(ee)
        if debug:
            print(e)
            print(user_chat_model)
        pass


from flask import Flask, send_from_directory
from flask_cors import CORS
from waitress import serve
import os
import threading

app = Flask(__name__)
CORS(app)

@app.route('/data/image/<filename>', methods=['GET', 'POST'])
def image_files(filename):
    print("用户请求文件：", filename)
    if os.path.exists(os.path.join('./data/image/', filename)):
        return send_from_directory('./data/image/', filename, as_attachment=True)
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
    
@app.route('/data/image/<emotion>/<filename>', methods=['GET', 'POST'])
def emoji_files(emotion,filename):
    print("用户请求文件：", emotion,"/",filename)
    if os.path.exists('./data/image/%s/%s'%(emotion,filename)):
        return send_from_directory('./data/image/%s'%emotion, filename, as_attachment=True)
    else:
        return 'File not found', 404

# 定义一个函数来启动Flask应用
def run_server():
    serve(app, host='127.0.0.1', port=4321, threads=10)

# 创建并启动新线程
print("启用本地文件传输服务...")
thread = threading.Thread(target=run_server)
thread.start()


print("读取配置文件...")
with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    setinfo = setting.read()
    setdir = json.loads(setinfo)
    draw_url = setdir["draw_url"]
    draw_key = setdir["draw_key"]
    draw_model = setdir["draw_model"]
    system_prompts = setdir["system_prompts"]
    chat_models = setdir["chat_models"]
    debug = setdir["debug"]
    triggers = setdir["triggers"]
    random_trigger = setdir["random_trigger"]
    AI_name = setdir["AI_name"]
    ban_names = setdir["ban_names"]
    root_ids = setdir["root_ids"]

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
1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日老爹在不？#split#”
2. 使用语音时按照格式 #split##voice/语言合成的内容##split# ，例如语音输出“你好”： #split##voice/你好##split#  (不要过多使用语音；使用语音时不可使用（括号）和特色字符)
3. 使用绘画功能时按照格式 #split##picture/绘画提示词##split# ，例如绘画一个女孩： #split##picture/one girl##split#  （除非明确要求否则不要绘画；绘画提示词尽力充实丰富，细节饱满详细，提示词使用英文单词）
4. 需要联网搜索时按照格式 #split##search/搜索关键词##split#，例如查询国内的新闻：#split##search/国内 新闻##split#  （关键词尽量多，详细，具体）
5. 每隔一段时间有重要的信息点需要写入长期记忆 #split##memory/写入的信息内容##split#，例如提到幻日是你的老爹：#split##memory/幻日是我老爹##split# （信息尽可能精简，不要写入有时效性的类似“明天是周天”的信息会失效造成干扰，不要写入[self_impression]下已经存在的内容）
6. 不想或者不需要回复信息时，只需要输出 #split##pass/None##split#，例如提到的信息与你无关-“@蓝莓 你是坏蛋”： #split##pass/None##split# (不要总是使用此操作拒绝回复)
7. 当需要发送表情包表达情绪时，按照格式 #split##emotion/情绪##split#，例如有人反复纠缠不休导致很生气：#split##emotion/angry##split#  (不要总是发送表情包，每条信息最多使用一次表情包，只支持以下表情包[angry,happy,sad,fear,bored])
8. 心情好或想要唱歌时，按照格式 #split##music/歌曲名##split#，例如有人想让你唱潮汐：#split##music/潮汐##split# (不要总是唱歌，男声或合唱可能声音可能出问题，可适当通过唱歌表达情绪)
9. 需要切换自身心情时，按照格式 #split##mood/心情名##split#，例如有人惹你生气：#split##mood/angry##split#，心情平复后：#split##mood/default##split#（不要频繁切换情感，只支持以下心情[{moodstr}]）
0. 回复时，禁止以群友的名义重复或冒充群友说话
"""

system_prompt=system_prompts["default"]
system= system_prompt+order

for mood in system_prompts.keys():
    system_prompts[mood]+=order

jieyue=True
cpu_lacking=False
weihu=False#是否暂停qq机器人进入维护状态
objdict={}
processed_d_data='想聊天'
startT=time.time()#总计时开始
print('程序已启动')

while 1:
    try:
        rev = rev_msg()
        try:
            botID=rev['self_id']
        except:
            pass
        if rev == None:
            continue
    except:
        continue
    Thread(target=main,args=(rev,)).start()


