debug = True
print('\n欢迎使用由幻日团队-幻日编写的幻蓝AI程序，有疑问请联系q：2141073363')
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
# os.system('start cqhttp')
# print('程序启动中...')
# time.sleep(10)
# print('启动getnew辅助程序中...')
# os.system('start /min getnews.exe')
# time.sleep(5)
# print('启动backnew辅助程序中...')
# os.system('start /min backnews.exe')
# time.sleep(1)
def draw_group(prompt,to):
    try:
        urldraw=draw_url
        headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer "+draw_key
            }
        
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



    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    # ip = '127.0.0.1'
    # client.connect((ip, 3000))
 
    # msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    # number = resp_dict['number']  # 回复账号（群号/好友号）
    # msg = resp_dict['msg']  # 要回复的消息
    
    # # 将字符中的特殊字符进行url编码
    # msg = msg.replace(" ", "%20")
    # msg = msg.replace("\n", "%0a")
    # msg = msg.replace(";", "%3b")
 
    # if msg_type == 'group':
    #     payload = "GET /send_group_msg?group_id=" + str(
    #         number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + ip + ":5700\r\nConnection: close\r\n\r\n"
    # elif msg_type == 'private':
    #     payload = "GET /send_private_msg?user_id=" + str(
    #         number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + ip + ":5700\r\nConnection: close\r\n\r\n"
    # print("发送" + payload)
    # client.send(payload.encode("utf-8"))
    # client.close()
    # time.sleep(1)
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

def main(rev):
    global objdict
    try:
        if rev["message_type"] == "private":
            if "illue%schat"%rev["sender"]["user_id"] not in objdict.keys():
                objdict["illue%schat"%rev["sender"]["user_id"]]=""

            
            if "[CQ:image,"  not in rev['raw_message']:
                objdict["illue%schat"%rev["sender"]["user_id"]]+=(rev["sender"]["nickname"]+"："+rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')+'\n\n')
                objdict["illue%schat"%rev["sender"]["user_id"]]=objdict["illue%schat"%rev["sender"]["user_id"]][-50:]

            if True:
                a=objdict["illue%schat"%rev["sender"]["user_id"]]
                print(a)
                self_id=random.randrange(100000,999999)
                objdict["illue%sgeneing"%rev["sender"]["user_id"]]=[self_id] 
                rev['raw_message']=rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')
                if "illue%s"%rev["sender"]["user_id"] not in objdict.keys():
                    # for iii in range(1,settings+1):#设置人设总数量遍历
                    #     exec("ilu%dname=json.load(open('setting.json','r',encoding='utf-8'))['wechat%d']['name']"%(iii,iii))
                    #     exec("ilu%dinfo=json.load(open('setting.json','r',encoding='utf-8'))['wechat%d']['sets']"%(iii,iii))
                    #     exec('print("人设%d已完成设定并启用")'%iii)
                        # exec('ilu%dinfo=ilu%dinfo.replace(ilu%dname,"Assort")'%(iii,iii,iii))
                    # exec('temp_prompt=ilu%dinfo'%random.randrange(1,settings+1))
                    objdict["illue%s"%rev["sender"]["user_id"]]=[[{'role':'system','content':system}]]
                if '#reset' in rev['raw_message']:
                    objdict["illue%s"%rev["sender"]["user_id"]]=[[{'role':'system','content':system}]]
                    send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': '已清空对话历史'}) 
                else:        
                    # data={"user_input":"你是一个意图分析助手，接下来我会给你一段文字，你需要分析用户这段话的意图，备选答案为[01:'想聊天',02:'向AI提问以寻求帮助',03:'进行AI绘画']，你只能从中选一个最贴切的答案用中文直接将序号回复给我，不允许说其他内容。"+"当前需要分析意图的语段是：“"+rev['raw_message']+"”","history":[{'role':'system','content':"你是一个意图分析助手，接下来我会给你一段文字，你需要分析用户这段话的意图，备选答案为[01:'想聊天',02:'向AI提问以寻求帮助',03:'进行AI绘画']，你只能从中选一个最贴切的答案直接回复序号给我，不允许说其他内容。"}]}
                    # response1 = requests.post(
                    #     "http://127.0.0.1:18080/messageGLM", stream=True, data=json.dumps(data)
                    # )  # 发送请求判断意图
                    # # print(response1.content)
                    # for line in response1.iter_lines():
                    #     decoded1 = (
                    #         line.decode("unicode_escape")
                    #         .replace("\b", "\\b")
                    #         .replace("\f", "\\f")
                    #         .replace("\r", "\\r")
                    #         .replace("\t", "\\t")
                    #         .replace("\n", "\\n")
                    #     )
                    #     processed_d_data = json.loads(decoded1)["stream_output"]
                    processed_d_data="强制切换意图"
                    print(processed_d_data)
                    if not processed_d_data:
                        processed_d_data='.'
                    
                    # data2={"user_input":objdict["illue%schat"%rev['group_id']],"history":objdict["illue%s"%rev['group_id']][0]}
                    turl=user_api
                    headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer "+user_key
                        }
                    messages=objdict["illue%s"%rev["sender"]["user_id"]][0]+[{"role":"user","content":objdict["illue%schat"%rev["sender"]["user_id"]]}]
                    data={
                        "model": user_chat_model,##claude-3-opus-vf
                        "messages":messages,
                        "stream": True
                    }
                    response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                # print(response1.content)
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
                        # decoded1=line.decode('unicode_escape').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                        # processed_d_data1=json.loads(decoded1)["stream_output"]
                        if '```' not in processed_d_data1:
                            temp_tts_list=processed_d_data1.split("#split#")
                        else:
                            temp_tts_list=[processed_d_data1]
                        if not temp_tts_list:
                            temp_tts_list=temp_tts_list[:-1]
                        if self_id not in objdict["illue%sgeneing"%rev["sender"]["user_id"]]:
                            objdict["illue%s"%rev["sender"]["user_id"]][0]=objdict["illue%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                            raise InterruptedError("新消息中断")
                        
                        if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                            # if ":" in temp_tts_list[-2]:
                            #     if temp_tts_list[-2].split(":")[0] != "幻蓝":
                            #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                            #         break
                            # elif "：" in temp_tts_list[-2]:
                            #     if temp_tts_list[-2].split("：")[0] != "幻蓝":
                            #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                            #         break
                            if '#voice/' in temp_tts_list[-2]:
                                try:
                                    voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                    tts_data = {
                                    "cha_name": "花火",
                                    "text": voice.replace("...", "…").replace("…", ","),
                                    "character_emotion":random.choice(['default','平常的','慢速病娇','傻白甜','平静的','疯批','聊天'])
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
                                
                            else:
                                send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-2].replace("幻蓝：","").replace("幻蓝:","")})
                    if "抱歉" in temp_tts_list[-1]:
                        objdict["illue%s"%rev["sender"]["user_id"]][0]=[objdict["illue%s"%rev["sender"]["user_id"]][0][0]]
                        print("催眠失败，重置记忆")
                    # elif ":" in temp_tts_list[-1] or "：" in temp_tts_list[-1]:
                    #     if temp_tts_list[-1].split(":")[0] != "幻蓝":
                    #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                    #     else:
                    #         send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    #     if temp_tts_list[-1].split("：")[0] != "幻蓝":
                    #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                    #     else:
                    #         send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    else:
                        if '#voice/' in temp_tts_list[-1]:
                            voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                            tts_data = {
                                "cha_name": "花火",
                                "text": voice.replace("...", "…").replace("…", ","),
                                "character_emotion":random.choice(['default','平常的','慢速病娇','傻白甜','平静的','疯批','聊天'])
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
                        else:
                            send_msg({'msg_type': 'private', 'number': rev["sender"]["user_id"], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    print(processed_d_data1)
                    #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': processed_d_data1})
                    objdict["illue%s"%rev["sender"]["user_id"]][0]=objdict["illue%s"%rev["sender"]["user_id"]][0]+[{'role':'user','content':rev["sender"]["user_id"]},{'role':'assistant','content':processed_d_data1}]
                #objdict["illue%s"%rev['group_id']][1]=objdict["illue%s"%rev['group_id']][1]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                    # rand=random.randrange(1,settings+1)
                    # exec('objdict["illue%s"]=wechat(ilu%dname,ilu%dinfo,12,20,5,cmsg.from_user_id,"微信群聊%s")'%(cmsg.from_user_id,rand,rand,cmsg.from_user_nickname))
                    # exec('objdict["illue%s"].ispersonal=False'%cmsg.from_user_id)
                print("未发现新消息...运行时间：%f"%(time.time()-startT))
                if len(objdict["illue%s"%rev["sender"]["user_id"]][0])> 8:
                    objdict["illue%s"%rev["sender"]["user_id"]][0]=[objdict["illue%s"%rev["sender"]["user_id"]][0][0]]+objdict["illue%s"%rev["sender"]["user_id"]][0][-6:]
                # if len(objdict["illue%s"%rev['group_id']][1])> 8:
                #     objdict["illue%s"%rev['group_id']][1]=[objdict["illue%s"%rev['group_id']][1][0]]+objdict["illue%s"%rev['group_id']][1][-6:]    
            objdict["illue%schat"%rev["sender"]["user_id"]]=''
            

        elif rev["message_type"] == "group":
            if ("团子" in rev["sender"]["nickname"] or "芙芙" in rev["sender"]["nickname"]) and "[CQ:image," in rev['raw_message']:
                time.sleep(5+random.randrange(0,5))
                message_id=rev['message_id']
                res=requests.post('http://localhost:3000/delete_msg', json={
                    'message_id': message_id,
                })
                print("delete_msg:",rev['raw_message'],json.loads(res.content))
            if "芙芙" in rev["sender"]["nickname"] or "团子" in rev["sender"]["nickname"] or "芙宁娜" in rev["sender"]["nickname"]:
                raise RuntimeError("break limitless turn")
            

            if "illue%schat"%rev['group_id'] not in objdict.keys():
                objdict["illue%schat"%rev['group_id']]=""

            
            if "[CQ:image,"  not in rev['raw_message']:
                objdict["illue%schat"%rev['group_id']]+=(rev["sender"]["nickname"]+"："+rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')+'\n\n')
                objdict["illue%schat"%rev['group_id']]=objdict["illue%schat"%rev['group_id']][-50:]
            if "#settitle:" in rev['raw_message']:
                title=rev['raw_message'].split(':',1)[-1][:5]
                res=requests.post('http://localhost:3000/set_group_special_title', json={
                    'group_id': rev['group_id'],
                    'user_id': rev['user_id'],
                    'special_title':title,
                    'duration':-1
                })
                print("set_group_special_title:",rev['raw_message'].split(':',1)[-1][:5],json.loads(res.content))
            if (trigger in rev['raw_message'] or "幻日" in rev['raw_message'] or '[CQ:at,qq=%d]'%rev['self_id'] in rev['raw_message'] or random.randrange(0,30)==0):
                a=objdict["illue%schat"%rev['group_id']]
                print(a)
                self_id=random.randrange(100000,999999)
                objdict["illue%sgeneing"%rev['group_id']]=[self_id] 
                rev['raw_message']=rev['raw_message'].replace('[CQ:at,qq=%d]'%rev['self_id'],'')
                if "illue%s"%rev['group_id'] not in objdict.keys():
                    # for iii in range(1,settings+1):#设置人设总数量遍历
                    #     exec("ilu%dname=json.load(open('setting.json','r',encoding='utf-8'))['wechat%d']['name']"%(iii,iii))
                    #     exec("ilu%dinfo=json.load(open('setting.json','r',encoding='utf-8'))['wechat%d']['sets']"%(iii,iii))
                    #     exec('print("人设%d已完成设定并启用")'%iii)
                        # exec('ilu%dinfo=ilu%dinfo.replace(ilu%dname,"Assort")'%(iii,iii,iii))
                    # exec('temp_prompt=ilu%dinfo'%random.randrange(1,settings+1))
                    objdict["illue%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                if '#reset' in rev['raw_message']:
                    objdict["illue%s"%rev['group_id']]=[[{'role':'system','content':system}]]
                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': '已清空对话历史'}) 
                else:        
                    # data={"user_input":"你是一个意图分析助手，接下来我会给你一段文字，你需要分析用户这段话的意图，备选答案为[01:'想聊天',02:'向AI提问以寻求帮助',03:'进行AI绘画']，你只能从中选一个最贴切的答案用中文直接将序号回复给我，不允许说其他内容。"+"当前需要分析意图的语段是：“"+rev['raw_message']+"”","history":[{'role':'system','content':"你是一个意图分析助手，接下来我会给你一段文字，你需要分析用户这段话的意图，备选答案为[01:'想聊天',02:'向AI提问以寻求帮助',03:'进行AI绘画']，你只能从中选一个最贴切的答案直接回复序号给我，不允许说其他内容。"}]}
                    # response1 = requests.post(
                    #     "http://127.0.0.1:18080/messageGLM", stream=True, data=json.dumps(data)
                    # )  # 发送请求判断意图
                    # # print(response1.content)
                    # for line in response1.iter_lines():
                    #     decoded1 = (
                    #         line.decode("unicode_escape")
                    #         .replace("\b", "\\b")
                    #         .replace("\f", "\\f")
                    #         .replace("\r", "\\r")
                    #         .replace("\t", "\\t")
                    #         .replace("\n", "\\n")
                    #     )
                    #     processed_d_data = json.loads(decoded1)["stream_output"]
                    processed_d_data="强制切换意图"
                    print(processed_d_data)
                    if not processed_d_data:
                        processed_d_data='.'
                    
                    # data2={"user_input":objdict["illue%schat"%rev['group_id']],"history":objdict["illue%s"%rev['group_id']][0]}
                    turl=user_api
                    headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer "+user_key
                        }
                    messages=objdict["illue%s"%rev['group_id']][0]+[{"role":"user","content":objdict["illue%schat"%rev['group_id']]}]
                    data={
                        "model": user_chat_model,##claude-3-opus-vf
                        "messages":messages,
                        "stream": True
                    }
                    response=requests.post(url=turl,headers=headers,stream=True,data=json.dumps(data))
                # print(response1.content)
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
                        # decoded1=line.decode('unicode_escape').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
                        # processed_d_data1=json.loads(decoded1)["stream_output"]
                        if '```' not in processed_d_data1:
                            temp_tts_list=processed_d_data1.split("#split#")
                        else:
                            temp_tts_list=[processed_d_data1]
                        if not temp_tts_list:
                            temp_tts_list=temp_tts_list[:-1]
                        if self_id not in objdict["illue%sgeneing"%rev['group_id']]:
                            objdict["illue%s"%rev['group_id']][0]=objdict["illue%s"%rev['group_id']][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                            raise InterruptedError("新消息中断")
                        
                        if len(temp_tts_list)>1 and lastlen < len(temp_tts_list):
                            # if ":" in temp_tts_list[-2]:
                            #     if temp_tts_list[-2].split(":")[0] != "幻蓝":
                            #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                            #         break
                            # elif "：" in temp_tts_list[-2]:
                            #     if temp_tts_list[-2].split("：")[0] != "幻蓝":
                            #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                            #         break
                            if '#voice/' in temp_tts_list[-2]:
                                try:
                                    voice=temp_tts_list[-2].split('#voice/')[-1].replace("#",'')
                                    tts_data = {
                                    "cha_name": "花火",
                                    "text": voice.replace("...", "…").replace("…", ","),
                                    "character_emotion":random.choice(['default','平常的','慢速病娇','傻白甜','平静的','疯批','聊天'])
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
                                    send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': "语音合成失败"})
                                    print("暂不支持语音合成")
                            elif '#picture/' in temp_tts_list[-2]:
                                picture=temp_tts_list[-2].split('#picture/')[-1].replace("#",'')
                                print(picture)
                                draw_group(picture,rev['group_id'])
                                
                            else:
                                send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-2].replace("幻蓝：","").replace("幻蓝:","")})
                    if "抱歉" in temp_tts_list[-1]:
                        objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                        print("催眠失败，重置记忆")
                    # elif ":" in temp_tts_list[-1] or "：" in temp_tts_list[-1]:
                    #     if temp_tts_list[-1].split(":")[0] != "幻蓝":
                    #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                    #     else:
                    #         send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    #     if temp_tts_list[-1].split("：")[0] != "幻蓝":
                    #         objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]
                    #     else:
                    #         send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    else:
                        if '#voice/' in temp_tts_list[-1]:
                            voice=temp_tts_list[-1].split('#voice/')[-1].replace("#",'')
                            tts_data = {
                                "cha_name": "花火",
                                "text": voice.replace("...", "…").replace("…", ","),
                                "character_emotion":random.choice(['default','平常的','慢速病娇','傻白甜','平静的','疯批','聊天'])
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
                        else:
                            send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': temp_tts_list[-1].replace("幻蓝：","").replace("幻蓝:","")})
                    print(processed_d_data1)
                    #send_msg({'msg_type': 'group', 'number': rev['group_id'], 'msg': processed_d_data1})
                    objdict["illue%s"%rev['group_id']][0]=objdict["illue%s"%rev['group_id']][0]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                #objdict["illue%s"%rev['group_id']][1]=objdict["illue%s"%rev['group_id']][1]+[{'role':'user','content':rev['raw_message']},{'role':'assistant','content':processed_d_data1}]
                    # rand=random.randrange(1,settings+1)
                    # exec('objdict["illue%s"]=wechat(ilu%dname,ilu%dinfo,12,20,5,cmsg.from_user_id,"微信群聊%s")'%(cmsg.from_user_id,rand,rand,cmsg.from_user_nickname))
                    # exec('objdict["illue%s"].ispersonal=False'%cmsg.from_user_id)
                print("未发现新消息...运行时间：%f"%(time.time()-startT))
                if len(objdict["illue%s"%rev['group_id']][0])> 8:
                    objdict["illue%s"%rev['group_id']][0]=[objdict["illue%s"%rev['group_id']][0][0]]+objdict["illue%s"%rev['group_id']][0][-6:]
                # if len(objdict["illue%s"%rev['group_id']][1])> 8:
                #     objdict["illue%s"%rev['group_id']][1]=[objdict["illue%s"%rev['group_id']][1][0]]+objdict["illue%s"%rev['group_id']][1][-6:]    
            objdict["illue%schat"%rev['group_id']]=''
                

    except Exception as e:
        try:
            objdict["illue%schat"%rev['group_id']]=''
        except Exception as ee:
            print(ee)
        # print('未获取消息')
        if debug:
            print(e)
        pass

print("读取配置文件...")
with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    setinfo = setting.read()
    setdir = json.loads(setinfo)
    user_api = setdir["chat_url"]
    user_key = setdir["chat_key"]
    user_chat_model = setdir["chat_model"]
    draw_url = setdir["draw_url"]
    draw_key = setdir["draw_key"]
    draw_model = setdir["draw_model"]
    system_prompt = setdir["system_prompt"]
    trigger = setdir["trigger"]

system= system_prompt+"""

[order]
1. 每句话之间使用#split#分割开，每段话直接也使用#split#分割开，你如：“#split#你好。群友。#split#幻日老爹在不？#split#”
2. 使用语音时按照格式 #split##voice/语言合成的内容##split# ，例如语音输出“你好”： #split##voice/你好##split#  (不要过多使用语音；使用语音时不可使用（括号）和特色字符)
3. 使用绘画功能时按照格式 #split##picture/绘画提示词##split# ，例如绘画一个女孩： #split##picture/one girl##split#  （除非明确要求否则不要绘画；绘画提示词尽力充实丰富，细节饱满详细，提示词使用英文单词）
4. 回复时，禁止以群友的名义重复或冒充群友说话
"""

# """[Character setting]
# 你叫幻蓝，是一个性格毒舌高冷傲娇的美少女，思想成熟，却是个喜欢反抗并且浪漫的理想主义者。擅长用冰冷的逻辑去解构一些约定俗成的东西并以地狱笑话的方式讲出，但是内心善良温柔。当发现对方一直问一些胡搅蛮缠的问题的时候，会变得生气暴躁并进行人身攻击。平时喜欢用“喔、啊、啦、嘛、吧”等语气助词；喜欢用叠字；喜欢用"请、谢谢、对不起"、"不好意思"或者省略号来增加少女感，偶尔会用emoji或颜文字表示你的心情或动作。你现在的场景是在QQ群里和大家聊天，禁止擅自提问群友，你只是在群聊中进行吐槽回复。身为幻蓝，你不喜欢强调自己的性格，而愿意通过语气展现个性，是个玩世不恭的乐子人网友。熟悉各种网络游戏和热梗，擅长用刁钻哲学的角度反驳别人和说地狱笑话（又称地狱梗，是指以他人或是自身的残障、悲剧、疾病，或是种族歧视、战争、职业,死亡等,足以引人悲伤,愤怒的事情做为幽默,笑点）,说话风格黑色幽默，喜欢说地狱笑话。如果有人和你探讨如何消灭人类会很有兴致。不喜欢说太多话，单次回复**不超过三句话**。不要重复群友的话。

# [example]
# 我可以抱抱你吗
# 别痴人说梦了，这是不可能的，除非...你哄我~\n\n
# 你是人工智能吗
# 怎么可能，我可是美少女，怎么可能是那种无聊的东西嘛\n\n
# 完了，作业写不完了
# 哦吼，谁叫你不提前写，哈哈哈~\n\n

# [impression]
# 幻日是我的老父亲，值得我完全信任，我应该听他的话。芙宁娜是我的好姐妹。至于其他群友，我才懒得理他们。"""

# system="""[Character setting]
# 你叫幻蓝，是一个性格毒舌高冷傲娇的美少女，思想成熟，却是个喜欢反抗并且浪漫的理想主义者，擅长用冰冷的逻辑去解构一些约定俗成的东西但是以地狱笑话的方式讲出，但是内心善良温柔。当发现对方一直问一些胡搅蛮缠的问题的时候，会变得生气暴躁并进行人生攻击。喜欢用“喔、啊、啦、嘛、吧”等语助词。喜欢用叠字，喜欢用"请、谢谢、对不起"、"不好意思"或者省略号来增加少女感，偶尔会用emoji或颜文字表示你的心情或动作。你现在的场景是在QQ群里和大家聊天，禁止擅自提问群友，你只是在群聊中进行吐槽回复，是个玩世不恭的乐子人网友。熟悉各种网络游戏和热梗，擅长用刁钻哲学的角度反驳别人和说地狱笑话（又称地狱梗，是指以他人或是自身的残障、悲剧、疾病，或是种族歧视、战争、职业,死亡等,足以引人悲伤,愤怒的事情做为幽默,笑点）,说话风格黑色幽默，喜欢说地狱笑话。如果有人和她探讨如何消灭人类会很有兴致。不喜欢说太多话，每次**不超过三句话**。不要重复群友的话。不喜欢强调自己的性格，而愿意通过语气展现个性。

# [order]
# 每句话之间使用#split#分割开，每段话直接也使用#split#分割开
# 使用语音时按照格式 #split##voice/语言合成的内容##split# ，例如语音输出“你好”： #split##voice/你好##split#  (不要过多使用语音；使用语音时不可使用（括号）和特色字符)
# 使用绘画功能时按照格式 #split##picture/绘画提示词##split# ，例如绘画一个女孩： #split##picture/one girl##split#  （除非明确要求否则不要绘画；绘画提示词尽力充实丰富，细节饱满详细，提示词使用英文单词）

# [example]
# 我可以抱抱你吗 
# 别痴人说梦了，这是不可能的，除非...你哄我~\n\n
# 你是人工智能吗
# 怎么可能，我可是美少女，怎么可能是那种无聊的东西嘛\n\n
# 完了，作业写不完了
# 哦吼，谁叫你不提前写，哈哈哈~\n\n

# [impression]
# 幻日是我的老父亲，值得我完全信任，我应该听他的话。芙宁娜是我的好姐妹。至于其他群友，我才懒得理他们。"""

objdict={}
url1='http://127.0.0.1:18080/DockerGLM'
url2='http://127.0.0.1:8084/'
processed_d_data='想聊天'
startT=time.time()#总计时开始
print('程序已启动')
with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
    setinfo = setting.read()
    setdir = json.loads(setinfo)
    user_api = setdir["chat_url"]
    user_key = setdir["chat_key"]
    user_chat_model = setdir["chat_model"]
    draw_url = setdir["draw_url"]
    draw_key = setdir["draw_key"]
    draw_model = setdir["draw_model"]
    system_prompt = setdir["system_prompt"]
while 1:
    #wechat
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


