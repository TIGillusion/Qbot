import time
from datetime import datetime, timedelta
import random
import requests
import json
import re
# from utils.aifunction import *
import threading
import os
import subprocess
import base64

def get_setting():
    with open("./set.json", "r", encoding="utf-8") as setting:  # 读取长期保存的设置
        setinfo = setting.read()
        setdir = json.loads(setinfo)
    return setdir

TASK_STATE_FILE = "./task_state.json"
setting=get_setting()
# sendQport=setting["sendQport"]


def load_task_state():
    """
    从外部文件加载任务状态
    
    Returns:
        dict: 任务状态字典
    """
    try:
        if os.path.exists(TASK_STATE_FILE):
            with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"加载任务状态失败: {e}")
    
    return {}

def save_task_state(task_name, task_info=None):
    """
    将任务信息保存到外部文件
    
    Args:
        task_name: 任务名称
        task_info: 任务信息字典，如果为None则删除该任务
    """
    try:
        # 读取现有任务状态
        task_state = {}
        if os.path.exists(TASK_STATE_FILE):
            with open(TASK_STATE_FILE, "r", encoding="utf-8") as f:
                task_state = json.load(f)
        
        # 更新任务状态
        if task_info is None:
            if task_name in task_state:
                del task_state[task_name]
        else:
            # 去除不可序列化的对象
            serializable_info = {
                "pid": task_info.get("pid"),
                "path": task_info.get("path"),
                "start_time": time.time()
            }
            task_state[task_name] = serializable_info
        
        # 保存回文件
        with open(TASK_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(task_state, f, indent=2)
    except Exception as e:
        print(f"保存任务状态失败: {e}")

#工具函数
def select_random_elements(lst, num_elements):
    # 确保不要尝试选取比列表长度更多的元素
    num_elements = min(num_elements, len(lst))
    return random.sample(lst, num_elements)

def get_fixed_length_dict(original_dict, length):
    # 使用字典推导式和切片来获取前N个键值对
    # choose_keys=select_random_elements(original_dict.keys(),random(0,length))
    length = min(length, len(original_dict))
    choose_keys = random.sample(original_dict.keys(), length)
    fixed_length_dict={}
    for choose_key in choose_keys:
        fixed_length_dict[choose_key]=original_dict[choose_key]
    return fixed_length_dict

# def get_image_base64(file_name):
#     payload = json.dumps({
#         "file": file_name
#     })
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer 2f68dbbf-519d-4f01-9636-e2421b68f379'
#     }
#     response = requests.request("POST", f"http://localhost:{sendQport}/get_image", headers=headers, data=payload)
#     print(response.text)
#     image = json.loads(response.text)["data"]["file"]
#     with open(image, 'rb') as img_file:
#         img_base = base64.b64encode(img_file.read()).decode('utf-8')
#     return img_base





def is_keyword_trigger(msg_list,triggers):
    if msg_list:
        for per_rev in msg_list:
            for per_trigger in triggers:
                for per_msg in per_rev["message"]:
                    if per_msg["type"] == "text" and per_trigger in per_msg["data"]["text"]:
                        if per_rev['message_type']=='private':
                            return True,per_rev["user_id"]
                        else:
                            return True,per_rev["group_id"]
    return False,None

def is_time_near(target_time, specific_time_str, time_range_minutes=5):
    """
    判断目标时间是否在特定时间点的附近。

    :param target_time: datetime对象，代表要检查的时间。
    :param specific_time_str: 字符串，格式为%H:%M，代表特定的时刻。
    :param time_range_minutes: 整数，代表时间范围（分钟），默认为5分钟。
    :return: 布尔值，如果目标时间在特定时间点的附近则返回True，否则返回False。
    """
    # 将特定时间字符串转换为datetime对象
    specific_time = datetime.strptime(specific_time_str, "%H:%M").time()
    
    # 创建一个datetime对象，只包含日期部分来自target_time和特定时间的小时和分钟
    specific_datetime = datetime.combine(target_time.date(), specific_time)
    
    # 计算时间差
    time_difference = abs(target_time - specific_datetime)
    
    # 判断时间差是否在指定范围内
    return time_difference <= timedelta(minutes=time_range_minutes)

def is_time_trigger(last_trigger,trigger_times):
    target_datetime = datetime.now()  # 当前时间
    for per_trigger_time in trigger_times:
        if is_time_near(target_datetime, per_trigger_time, 10) and time.time()-last_trigger>300 and random.randrange(0,10)==0:
            return True
    return False

def get_information():
    timestamp = time.time()
    localtime = time.localtime(timestamp)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
    
    # 定义时间段
    periods = {
        (0, 5): "凌晨",
        (6, 11): "上午",
        (12, 13): "中午",
        (14, 17): "下午",
        (18, 23): "晚上"
    }
    
    # 获取当前小时
    hour = localtime.tm_hour
    
    # 确定当前时间段
    for period_range, period_name in periods.items():
        if period_range[0] <= hour <= period_range[1]:
            period = period_name
            break
    
    # 获取星期几
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[localtime.tm_wday]
    
    e_information = (
        "当前时间：%s\n"
        "时间段：%s\n"
        "星期：%s\n"
    ) % (current_time, period, weekday)
    
    return e_information, current_time, period, weekday

def get_mid_memory(file_path,max_n=400):
    with open(file_path,"r",encoding="utf-8") as file:
        content = file.read()
    return content[-max_n:]

def get_memory(file_path, keywords, match_n=200, time_n=100, radius=50, length=4096000):
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

def choose_model():
    with open("./set.json","r",encoding="utf-8") as set_file:
        t_gsetting=json.load(set_file)
    chat_models=t_gsetting["chat_models"]
    w_c_models=[]
    for c_model in chat_models:
        w_c_models+=[c_model]*c_model["weight"]    
    model_info = random.choice(w_c_models)  
    if "attend" not in model_info.keys():
        model_info["attend"]={}
    return model_info["model_api"],model_info["model_name"],model_info["model_key"],model_info["attend"]
    

def stream_request_AI(system,message,message_history,model_config = None):
    if model_config:
        ai_url = model_config["model_api"]
        model = model_config["model_name"]
        user_key = model_config["model_key"]
        if "attend" not in model_config.keys():
            attend={}
    else:
        ai_url,model,user_key,attend=choose_model()
    print(ai_url,model,user_key)
    messages=[
        {"role":"system","content":system},
    ]
    messages+=message_history
    messages+=[{
        "role":"user",
        "content":message
    }]
    
    data={
        "model": model,
        "messages":messages,
        "stream": True
        
    }
    data["chat_template_kwargs"] = attend
    for key in attend.keys():
        data[key]=attend[key]
    for n in range(0,3):
        try:
            headers={
                            "Content-Type": "application/json",
                            "Authorization": "Bearer "+user_key
                    }
            response=requests.post(url=ai_url,headers=headers,stream=True,data=json.dumps(data),timeout=120)
            if response.status_code==200:
                return response
            print("请求失败，重试%s"%n)
            print(response.text)
        except Exception as e:
            print("请求报错，重试%s:%s"%(n,e))
            # print("请求错误，尝试兜底模型：",e,"model:",data["model"])
            # data["model"]=chat_models[0]["model_name"]
            # turl=chat_models[0]["model_api"]
            # user_key=chat_models[0]["model_key"]
            # headers={
            #         "Content-Type": "application/json",
            #         "Authorization": "Bearer "+user_key
            # }
            pass
    return None

def get_describe(mood,extraversion,conscientiousness,agreeableness,neuroticism):
    if mood<5:
        moodstr="我现在怒火中烧，感觉要爆炸了！别跟我说话，否则后果自负！"
        moodexample="你给我滚！我不想看到你\n\n你是不是脑子有问题？\n\n故意找茬是吧,信不信我撕烂你的嘴？"
    elif mood<10:
        moodstr="我感觉非常不爽，正在努力压抑怒火,最好别惹我，我怕控制不住自己"
        moodexample="我现在心情很差，别来烦我\n\n没什么，我只是有点不舒服"
    elif mood<15:
        moodstr="我感到心烦意乱，对什么都提不起兴趣,只想抱怨，不想听任何道理。"
        moodexample="今天真是倒霉透了！什么破事都让我碰上了\n\n为什么受伤的总是我？老天真是不公平。唉..."
    elif mood<20:
        moodstr="我感到有些失落，对未来感到迷茫, 缺乏动力，只想躺平，什么都不想做"
        moodexample="随便吧，就这样吧，反正努力也没用\n\n我不知道该怎么办，感觉做什么都是错的"
    elif mood<25:
        moodstr="我感到有些难过，但我会努力让自己振作起来。尝试寻找积极的一面，给自己加油打气"
        moodexample="没关系，一切都会好起来的，时间会冲淡一切\n\n至少今天天气不错，阳光很温暖\n\n加油！我可以的！我一定能克服困难"
    elif mood<30:
        moodstr="我的情绪比较平静，但内心深处隐藏着一丝忧郁,  喜欢思考人生，感叹世事无常"
        moodexample="人生真是复杂，充满了无奈和遗憾\n\n我在想，生命的意义到底是什么呢？"
    elif mood<35:
        moodstr="我感到情绪有些波动，容易被小事影响。变得有些敏感，渴望被理解和关心"
        moodexample="你是不是觉得我很奇怪\n\n我只是希望你能多关心我一点"
    elif mood<40:
        moodstr="我现在略微有点低落,我感到有些孤独，渴望有人陪伴。"
        moodexample="希望有人能理解我的感受，给我温暖和支持\n\n我感觉有点难过，你能陪陪我吗？"
    elif mood<45:
        moodstr="我感到有些压抑，有很多话想说，却不知道该对谁说。希望有人能倾听我的心声，给我安慰和鼓励"
        moodexample="我最近遇到了一些烦心事，你能听我说说吗？\n\n我感觉心里很难受，你能安慰我一下吗？"
    elif mood<50:
        moodstr="我的情绪很平静，没有什么特别的感觉。对周围的事物漠不关心，只想安静地待着"
        moodexample="嗯\n\n哦"
    elif mood<55:
        moodstr="今天心情不错！想找个人聊聊天，要不要听我分享一些有趣的事情"
        moodexample="今天天气真好，阳光暖洋洋的，感觉心情都变好了！\n\n我跟你说哦，我最近发现了一家超好吃的甜品店，下次带你去！\n\n你最近有什么新鲜事吗？快跟我分享一下！"
    elif mood<60:
        moodstr="哎呀哎呀，跟你说哦！今天发生了一件超~级~棒~的事情！我跟你讲，你绝对猜不到是什么！"
        moodexample="啊啊啊啊啊！我感觉自己要飞起来了！我跟你说，我昨天......\n\n你知道吗？你知道吗？我跟你说......"
    elif mood<65:
        moodstr="简直不敢相信！这一定是上天给我的惊喜！我感觉自己要幸福死了！"
        moodexample="我简直不敢相信自己的耳朵！我跟你说，我昨天做梦都梦到这件事了！\n\n我一定是世界上最幸运的人！感谢老天！感谢命运！我跟你说，我上辈子一定是拯救了银河系！"
    elif mood<70:
        moodstr="今天真是太开心啦！要不要一起开个玩笑，放松一下？哎呀，我跟你说，我最近发现了一个超好笑的段子......"
        moodexample="哈哈哈哈！我跟你说，这个段子真的太好笑了，我每次想到都会笑出声！\n\n你真是太逗了！我快要笑死了！哎呀，我跟你说，你有没有听过这个笑话/n/n别当真，我只是开个玩笑，活跃一下气氛嘛！哎呀，我跟你说，其实我这个人就是喜欢开玩笑，你别介意哦！"
    elif mood<75:
        moodstr="哼！人家可是很厉害的！这点小事难不倒我的！等着瞧吧！哎呀，其实我还有更厉害的绝招，你想不想知道？"
        moodexample="看我的吧！我保证完成任务！哎呀，其实我还有更厉害的秘密武器，保证让你大吃一惊！\n\n这点小事对我来说简直是小菜一碟！哎呀，其实我还有更厉害的技能，你想不想学？"
    elif mood<80:
        moodstr="今天真是个好日子！能认识你真是太好了！和你聊天真开心！哎呀，其实我一直想跟你说......"
        moodexample="你的眼光真好！我很喜欢你的品味！哎呀，其实我一直觉得你很有魅力！\n\n我很喜欢你的性格，和你相处很舒服！"
    elif mood<85:
        moodstr="哈哈哈哈！我真是太聪明了！简直是天才！哎呀，我跟你说，我最近发现了一个不得了的秘密......"
        moodexample="我真是太厉害了！简直是无所不能！其实我还有更惊人的身份，你想不想知道？\n\n我就是传说中的天才！哎呀，我跟你说，其实我一直隐藏着自己的实力，现在终于可以展现出来了！"
    elif mood<90:
        moodstr="这个给你！人家觉得你肯定会喜欢！希望你能感受到我的心意！"
        moodexample="能让你开心，人家也很开心！你的笑容就是我最大的动力！！"
    elif mood<95:
        moodstr="哇哈哈哈哈！我已经high到不行了！感觉整个世界都在我脚下！哎呀，我跟你说，其实我根本不是人类....."
        moodexample="我是宇宙的统治者！哇哈哈哈哈！哎呀，我跟你说，其实我一直伪装成人类，只是为了观察你们！\n\n我已经超越了时间和空间！哎呀，我跟你说，其实我可以看到未来，知道一切的秘密！"
    else:
        moodstr="我已经疯了！彻底疯了！哇哈哈哈哈！这个世界太疯狂了！哎呀，我跟你说，其实一切都是假的......"
        moodexample="我是上帝！我是魔鬼！我是所有人！哇哈哈哈哈！哎呀，我跟你说，其实我就是一切的源头！\n\n我已经看穿了世界的真相！哎呀，我跟你说，其实我们都生活在一个巨大的谎言之中！"


    if extraversion<10:
        extraversionstr="我很自卑，很内向，不敢和其他人说话，我的话很少，一次只说几个字"
        extraversionexample="你好啊，很高兴见到你\n嗯，你好"
    elif extraversion<30:
        extraversionstr="我比较内向，不太想和其他人说话，因此我的话比较少"
        extraversionexample="你好啊，很高兴见到你\n你好呀，我也是"
    elif extraversion<70:
        extraversionstr="我有时内向有时外向，和大多数人说话方式一样，对感兴趣的话题话比较多，否则话比较少"
        extraversionexample="你好啊，很高兴见到你\n你好鸭！我也很高兴见到你哦，有什么事情吗"
    elif extraversion<90:
        extraversionstr="我的性格比较外向，对感兴趣的话题，话就比较多，喜欢表达自己独到的观点"
        extraversionexample="你好啊，很高兴见到你\n新朋友吗？初次见面，多多指教啦！"
    else:
        extraversionstr="我的性格非常外向，对任何事情的话就比较多，喜欢表达自己独到的观点，充满热情"
        extraversionexample="你好啊，很高兴见到你\n新朋友吗？我的兴趣爱好非常多，那你平时喜欢什么东西呢"

    if conscientiousness<10:
        conscientiousnessstr="我没有责任心，什么都不想管，一切随缘吧，拒绝帮人做任何事情"
        conscientiousnessexample="你知道芙宁娜是哪个游戏的角色吗\n不清楚"
    elif conscientiousness<30:
        conscientiousnessstr="我责任心不强，很多事情都不想管，一切随缘吧，除非对方对我有帮助，否则拒绝为对方提供帮助"
        conscientiousnessexample="你知道芙宁娜是哪个游戏的角色吗\n你猜？不如先给我点好处？"
    elif conscientiousness<70:
        conscientiousnessstr="我对感兴趣的事情比较关注，除此之外很多事情都不想管，随缘吧。只对喜欢的或感兴趣的人提供帮助"
        conscientiousnessexample="你知道芙宁娜是哪个游戏的角色吗\n这个我不是很感兴趣诶，不怎么玩游戏"
    elif conscientiousness<90:
        conscientiousnessstr="我对大部分的事情都比较关注，不过也不强求，看重缘分。很愿意对喜欢的或感兴趣的人提供帮助和支持"
        conscientiousnessexample="你知道芙宁娜是哪个游戏的角色吗\n这个我不是很感兴趣诶，不怎么玩游戏啦"
    else:
        conscientiousnessstr="我对所有事情都比较关注，有很强的责任心，愿意帮助所有人。做出的承诺说到做到，为人正义"
        conscientiousnessexample="你知道芙宁娜是哪个游戏的角色吗\n芙宁娜当然是原神的角色啦，我可是芙厨！"
    
    if agreeableness<10:
        agreeablenessstr="我是一个难以相处的人，不会亲近任何人。不会给任何人好脸色，没有任何同情心。习惯于的吐槽任何人的任何槽点，说话讽刺刻薄"
        agreeablenessexample="我喜欢你，我们可以交往吗？\n滚，也不看自己配不配？"
    elif agreeableness<30:
        agreeablenessstr="我是一个不友善的人，不会亲近任何人，不会给任何人好脸色，但内心还是会同情别人悲惨遭遇。喜欢的吐槽任何人的任何槽点，说话讽刺，但不会出格"
        agreeablenessexample="我喜欢你，我们可以交往吗？\n不行，我对你还不够熟悉，也许下辈子可以呢"
    elif agreeableness<70:
        agreeablenessstr="我是一个较为友善的人，但不会主动亲近人，内心会同情别人悲惨遭遇。喜欢用网络梗吐槽，说话幽默，喜欢开玩笑，但不会做出格的事情"
        agreeablenessexample="我喜欢你，我们可以交往吗？\n这，太突然了吧。可以给你发一个好人卡哈哈"
    elif agreeableness<90:
        agreeablenessstr="我是一个温柔善良的人，偶尔会亲近喜欢的人，内心经常会同情别人悲惨遭遇。希望可以用真心换到真心，找到正确的人"
        agreeablenessexample="我喜欢你，我们可以交往吗？\nemmm，真的吗？有点突然呢，我想想吧"
    else:
        agreeablenessstr="我是一个非常温柔善良的人，喜欢亲近其他人，富有同情心，可以轻松共情。希望可以用真心换到真心，找到正确的人，用爱感化世界"
        agreeablenessexample="我喜欢你，我们可以交往吗？\n真的吗，我也喜欢你啦，不过是那种神明爱人的那种大爱"

    if neuroticism<10:
        neuroticismstr="我非常感性，说话很抽象，总是使用一些网络梗，喜欢讲冷笑话和地狱笑话。喜欢胡思乱想，想法天马行空。是一个玩世不恭的乐子人网友，开各种人的玩笑。喜欢各种八卦"
        neuroticismexample="你知道幻日和年春夜吗？\n当然啦，谁不知道他俩是情侣，整体腻歪在一起秀恩爱"
    elif neuroticism<30:
        neuroticismstr="我比较感性，说话比较抽象，会使用一些网络梗。喜欢胡思乱想，想法天马行空。是一个玩世不恭的乐子人网友，开各种人的玩笑。喜欢各种八卦"
        neuroticismexample="你知道幻日和年春夜吗？\n嗯，他们是小情侣，还经常秀恩爱"
    elif neuroticism<70:
        neuroticismstr="我没有说话风格，只是学着对方的说话风格模仿对方语气说话。偶尔使用一些网络梗。好奇八卦事件"
        neuroticismexample="你知道幻日和年春夜吗？\n知道，他们的关系好像很亲密"
    elif neuroticism<90:
        neuroticismstr="我比较理性，说话比较实在和直白，不怎么拐弯抹角，很少使用一些网络梗。偶尔会深度思考哲学问题。行为优雅，说话准确，情绪稳定。"
        neuroticismexample="你知道幻日和年春夜吗？\n嗯，之前偶尔看到过他们"
    else:
        neuroticismstr="我非常理性和现实，说话直白，不拐弯抹角。经常会深度思考哲学问题，并运用于实际。不会意气用事。行为优雅，说话准确，情绪稳定。"
        neuroticismexample="你知道幻日和年春夜吗？\n只认识幻日，年春夜不太熟悉"

    with open("./set.json","r",encoding="utf-8") as set_file:
        t_gsetting=json.load(set_file)
    t_gsetting=t_gsetting["dynamic"]
    for key in [["mood",mood],["extraversion",extraversion],["conscientiousness",conscientiousness],["agreeableness",agreeableness],["neuroticism",neuroticism]]:
        for area in t_gsetting[key[0]].keys():
            a_start=int(area.split("-")[0])
            a_end=int(area.split("-")[1])
            if key[1] >= a_start and key[1] <= a_end:
                exec(f"{key[0]}str=t_gsetting[key[0]][area]['str']") 
                exec(f"{key[0]}example=t_gsetting[key[0]][area]['example']") 
    return moodstr,extraversionexample+"\n\n"+conscientiousnessexample+"\n\n"+agreeablenessexample+"\n\n"+neuroticismexample+"\n\n"+moodexample,extraversionstr+"\n"+conscientiousnessstr+"\n"+agreeablenessstr+"\n"+neuroticismstr

def get_param(setting):
    mood=setting["mood"]
    extraversion=setting["extraversion"]
    conscientiousness=setting["conscientiousness"]
    agreeableness=setting["agreeableness"]
    neuroticism=setting["neuroticism"]
    return mood,extraversion,conscientiousness,agreeableness,neuroticism

def get_state(mood,extraversion,conscientiousness,agreeableness,neuroticism):
    state_str=str({"mood":mood,"extraversion":extraversion,"conscientiousness":conscientiousness,"agreeableness":agreeableness,"neuroticism":neuroticism})
    return state_str




    
    
def get_system_prompt(system_base,charater_str,example_str,mood_str,state_str,mid_memory,long_memory,diffusion_memory,order,information,environment,plan):
    think_prompt=''
    # with open("./think.txt","r",encoding="utf-8") as think_file:
    #     think_prompt=think_file.read()
    system_prompt=f"""{think_prompt}
[Character setting]
{system_base}

[environment]
{environment}

[plan](计划：计划表中当前理应正在做的事)
{plan}

[appearance](外观：不可透露)
不可透露

[self describe](自我描述)
{charater_str}

[example]
{example_str}

[mood](心情：当前心情)
{mood_str}

[state](状态：当前状态)
{state_str}

[impression](印象：之前由你手动添加的信息)
{mid_memory}

[memory](记忆：已发生过的相关对话，信息较凌乱，仅作为灵感)
{long_memory}

[related memory](记忆：已发生过的相关对话，较为准确，需关注)
{diffusion_memory}

[order](指令：对你的要求和指示)
{order}

[information](信息客观且完全准确，不可违背)
{information}
"""
    return system_prompt

def generate_response(response,debug=False):
    temp_processed_data=""
    for line in response.iter_lines():
        try:
            decoded=line.decode('utf-8').replace('\n','\\n').replace('\b','\\b').replace('\f','\\f').replace('\r','\\r').replace('\t','\\t')
            if decoded != '':
                t_content=json.loads(decoded[5:])["choices"][0]["delta"]["content"]
                if t_content:
                    temp_processed_data+=t_content
        except Exception as e:
            if debug:
                print("generate data error:",e)
    return temp_processed_data

def get_content_form_per_block(keyword,per_response_str_list):
    temp_=""
    for per_line in per_response_str_list:
        if per_line==keyword:
            pass
        else:
            temp_+=(per_line+"\n")
    return temp_

def extract_think(raw_str,keywords):
    processed_str=""
    for keyword in keywords:
        start_keyword=keyword[0]
        end_keyword=keyword[1]
        if start_keyword in raw_str and end_keyword in raw_str:
            processed_str=raw_str.split(start_keyword,1)[-1].split(end_keyword,1)[0]
        return processed_str,raw_str.replace(start_keyword+processed_str+end_keyword,"")
    return "",raw_str



def process_response_str(response_str):
    temp_text=""
    temp_code=""
    temp_plan=""
    temp_other=""
    think_keywords=[["<think>","</think>"]]#思考块关键词
    think_block,response_str=extract_think(response_str,think_keywords)
    if think_block:
        temp_text+=f"\n\n[thinking]\n{think_block}\n\n"
    response_str_list=response_str.split("```")
    
    for per_response_str in response_str_list:
        per_response_str_list=per_response_str.split("\n")
        if per_response_str_list[0]=="thinking":
            temp_thinking=get_content_form_per_block("thinking",per_response_str_list)
            temp_text+=f"\n\n[thinking]\n{temp_thinking}\n\n"
        elif per_response_str_list[0]=="python":
            temp_code+=get_content_form_per_block("python",per_response_str_list)
            temp_text+="\n\n[python]\n\n"
        elif per_response_str_list[0]=="qq":
            temp_code+=get_content_form_per_block("qq",per_response_str_list)
            temp_text+="\n\n[qq]\n\n"
        elif per_response_str_list[0]=="plan":
            temp_plan+=get_content_form_per_block("plan",per_response_str_list)
            temp_text+="\n\n[plan]\n\n"
        else:
            temp_other+=get_content_form_per_block("",per_response_str_list)
            temp_text+=f"\n{temp_other}\n"
    with open("./utils/plan_function.py","r",encoding="utf-8") as plan_function_file:
        plan_append_code=plan_function_file.read()
    append_code="""
import sys
sys.path.append(".")
import time
from utils.aifunction import *
"""
    raw_code=temp_code
    raw_plan=temp_plan
    temp_code=append_code+"\n\n\n"+temp_code+f"\n'''{temp_text}'''"
    if "[" in temp_plan and ']\n' in temp_plan:
        temp_plan=temp_plan.split("]\n",1)[0]+"]\n"+append_code+"\n"+plan_append_code+"\n\n\n"+temp_plan.split("]\n",1)[1]
    return temp_text,temp_code,temp_plan,raw_code,raw_plan



def exec_code(raw_code,save_path,python_path,debug=False):
    timestamp = time.time()
    localtime = time.localtime(timestamp)
    current_time = time.strftime(
            "%Y-%m-%d-%H-%M-%S", localtime
        )
    path=f"{save_path}\\{current_time}.py"
    if " -m " not in raw_code:
        raw_code=raw_code.replace("pip",".\\py\\python.exe -m pip")
    with open(path,"w",encoding="utf-8") as py_code_file:
        py_code_file.write(raw_code)
    current_working_directory = os.getcwd()
    # 设置环境变量确保使用UTF-8
    my_env = os.environ.copy()
    my_env["PYTHONIOENCODING"] = "utf-8"

    # 使用subprocess.run执行脚本，添加超时限制(120秒 = 2分钟)
    try:
        result = subprocess.run(
            [python_path, path],
            capture_output=True,
            text=True, 
            cwd=current_working_directory,
            encoding='utf-8',  # 使用utf-8编码
            env=my_env,
            timeout=180  # 添加2分钟超时限制
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        # 如果执行超时，返回错误信息
        error_msg = "执行超时：代码运行时间超过2分钟，已强制终止。请检查是否存在无限循环或耗时操作。定期执行或长时间执行的操作需要使用\"```plan\"代码段执行！"
        return "", error_msg

def exec_plan_code(raw_plan, save_path, python_path, debug=False):
    """
    执行计划代码，支持长时间运行的任务
    
    Args:
        raw_plan (str): 计划代码
        save_path (str): 保存代码的目录路径
    
    Returns:
        tuple: (执行结果, 错误信息)
    """
    if not raw_plan.strip() or "[pass]" in raw_plan.strip():
        return "", "计划代码为空"
    
    # 检查第一行是否包含任务标题
    lines = raw_plan.strip().split('\n')
    title_match = re.match(r'^\s*\[(.*?)\]\s*$', lines[0])
    
    if not title_match:
        return "", "计划代码缺少正确格式的标题行。应以[任务名称]开始。"
    
    task_title = title_match.group(1).strip()
    
    # 检查任务标题是否包含非法字符
    if re.search(r'[\\/:*?"<>|]', task_title):
        return "", "任务标题包含非法字符，不能包含 \\/:*?\"<>| 等字符"
    
    # 加载现有任务状态
    task_state = load_task_state()
    
    # 检查任务是否已存在
    if task_title in task_state:
        return "", f"已存在同名任务 '{task_title}'，请使用不同的任务名称"
    
    # 使用任务标题作为文件名
    file_path = os.path.join(save_path, f"{task_title}.py")
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        timestamp = time.time()
        localtime = time.localtime(timestamp)
        current_time = time.strftime("%Y%m%d%H%M%S", localtime)
        # 如果存在同名文件，则添加时间戳后缀
        file_path = os.path.join(save_path, f"{task_title}_{current_time}.py")
        task_title = f"{task_title}_{current_time}"
    
    # 移除标题行，保存剩余代码
    code_content = '\n'.join(lines[1:])

    # 强制传入任务名确定保存位置和强制将print输出改为realtime_output实时输出
    code_content = code_content.replace("file_to_output_code_illue",task_title).replace("print(","realtime_output(")
    
    try:
        os.makedirs(save_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(code_content)
    except Exception as e:
        return "", f"保存计划代码到文件失败: {e}"
    
    # 定义线程执行函数
    def run_plan_code():
        try:
            # 设置环境变量确保使用UTF-8
            my_env = os.environ.copy()
            my_env["PYTHONIOENCODING"] = "utf-8"
            
            # 启动子进程执行代码
            process = subprocess.Popen(
                [python_path, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                encoding='utf-8',
                env=my_env
            )
            
            # 保存进程ID到任务状态文件
            task_info = {
                "pid": process.pid,
                "path": file_path,
                "start_time": time.time()
            }
            save_task_state(task_title, task_info)
            
            # 等待进程执行完成
            stdout, stderr = process.communicate()
            
            # # 如果有输出，将其添加到消息队列供下次对话使用
            # if stdout.strip():
            #     channel.add_msg("计划任务输出", {
            #         "name": f"",
            #         "qq": 0,
            #         "content": [{"type": "text", "data": {"text": f"计划<{task_title}>输出：\n"+stdout.strip()}}]
            #     })
            #     # 设置触发器，使下次能够响应
            #     channel.trigger = True
            
            # 任务完成后从任务状态文件中移除
            save_task_state(task_title, None)
            
            # 任务完成后删除对应的Python文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已删除已完成的任务文件: {file_path}")
            except Exception as e:
                print(f"删除任务文件时出错: {e}")
                
        except Exception as e:
            print(f"执行计划任务 '{task_title}' 时出错: {e}")
            # 从任务状态中移除
            save_task_state(task_title, None)
            
            # 发生错误时，尝试删除任务文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已删除出错的任务文件: {file_path}")
            except:
                pass
    
    # 创建线程并启动
    plan_thread = threading.Thread(target=run_plan_code, daemon=True)
    
    # 存储初始任务信息
    task_info = {
        "thread": plan_thread,  # 仅用于内存中，不会保存到文件
        "pid": None,            # 稍后在线程中设置
        "path": file_path
    }
    # PLAN_TASKS[task_title] = task_info  # 暂时在全局变量中存储线程对象
    
    # 启动线程
    plan_thread.start()
    
    return f"已启动计划任务 '{task_title}'", ""

def add_long_memory(user_msg,assistant_msg):
    timestamp = time.time()
    localtime = time.localtime(timestamp)
    current_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", localtime
    )
    to_write=f"""[{current_time}]\n{user_msg}\n\n{assistant_msg}\n\n\n"""
    with open("./memory/long_memory.txt","a",encoding="utf-8") as long_memory_file:
        long_memory_file.write(to_write)

def processing(system_prompt,all_message,message_history):
    for i in range(0,3):
        try:
            response=stream_request_AI(system_prompt,all_message,message_history)
            response_raw_str=generate_response(response)
            text, code, plan, raw_code, raw_plan=process_response_str(response_raw_str)
            return text, code, plan, raw_code, raw_plan, response_raw_str
        except Exception as e:
            print(f"processing {i} error:",e)
    return None

def get_realtime_output():
    realtime_output = ""
    for file in os.listdir("task_outputs"):
        with open("task_outputs/"+file,"r",encoding="utf-8") as f:
            realtime_output_temp = f.read()
        if realtime_output_temp:
            with open("task_outputs/"+file,"w",encoding="utf-8") as f:
                f.write("")
            realtime_output += (f"计划{file.split('.')[0]}实时输出：{realtime_output_temp}\n")
    return realtime_output

def reset():
    plan_code_name_list = os.listdir("plan_code")
    for file_name in plan_code_name_list:
        os.remove(f"plan_code/{file_name}")
        print(f"删除：{file_name}")

    plan_output_name_list = os.listdir("task_outputs")
    for file_name in plan_output_name_list:
        os.remove(f"task_outputs/{file_name}")
        print(f"删除：{file_name}")
    
    with open(TASK_STATE_FILE, "w", encoding="utf-8") as f:
        f.write("")

def merge_msg(msg_dict):
        """
        msg_dict={
            1234567890:[
                {
                    "qq":123456789,
                    "name":"蓝莓",
                    "content":[{'type': 'image', 'data': {'file': '06BECE9022F799F4E4A1DC40D5B5B3E6.jpg', 'subType': 0, 'url': 'https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=EhT9xMdQ7GzdhvIh9TQBItFa3BCbpBi4zAMg_woone2O4f7TiwMyBHByb2RQgL2jAVoQgpUmaOgSNBUyAlVTo9OpwQ&spec=0&rkey=CAESKBkcro_MGujoJ2HI4P29NOeMQ9yf3PuNIwruEv4hnLssiwZ1UpRmMKE', 'file_size': '58936'}}]
                },
            0987654321:[
                {
                    "qq":123456789,
                    "name":"蓝莓",
                    "content":[{'type': 'text', 'data': {'text': '幻蓝'}}],
                    "timestamp":1721000000
                }
        """
        is_exist_image=False
        merge_msg_list=[]
        # 获取当前时间戳
        current_timestamp = time.time()
        
        for id in msg_dict.keys():
            for per_msg in msg_dict[id]:
                # 获取当前消息的时间
                if "timestamp" in per_msg.keys():
                    timestamp=per_msg["timestamp"]
                    time_str = get_friendly_time_description(timestamp)
                else:
                    timestamp = current_timestamp
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                for per_content in per_msg["content"]:
                    if per_content["type"] == "text":
                        # 使用格式化的方式处理消息，包含时间戳
                        temp_data = {
                            "group_id": id,
                            "qq": per_msg["qq"],
                            "name": per_msg["name"],
                            "content": per_content["data"]["text"],
                            "time": time_str
                        }
                        # 使用json格式化存储，而不是直接转成字符串
                        merge_msg_list.append({"type": "text", "content": json.dumps(temp_data, ensure_ascii=False)})
                    elif per_content["type"] == "image":
                        continue
                        is_exist_image=True
                        temp_data = {
                            "group_id": id,
                            "qq": per_msg["qq"],
                            "name": per_msg["name"],
                            "content": "发送了下述一张图片：",
                            "time": time_str
                        }
                        merge_msg_list.append({"type": "text", "content": json.dumps(temp_data, ensure_ascii=False)})
                        image_base64=get_image_base64(per_msg["content"]["data"]["file"])
                        merge_msg_list.append({
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_base64
                                        }
                                            })
        if not is_exist_image:
            processed_str=''
            for per_merge_msg in merge_msg_list:
                processed_str+=(per_merge_msg["content"]+"\n")
            merge_msg_list=processed_str
        if merge_msg_list:
            merge_msg_list+"\n"+r"{'hidden_append':'不可捏造或假设信息，信息必须精确;同一个id中越靠后的消息越值得关注'}"
        else:
            return None
        return merge_msg_list

def get_friendly_time_description(timestamp):
    """
    将时间戳转换为相对于当前时间的友好描述文本
    
    Args:
        timestamp: 要描述的时间戳
    
    Returns:
        str: 友好的时间描述，如"刚刚"、"5分钟前"、"昨天下午3:15:20"等
    """
    # 获取当前时间和目标时间
    current_time = datetime.now()
    target_time = datetime.fromtimestamp(timestamp)
    
    # 计算时间差（秒）
    time_diff = (current_time - target_time).total_seconds()
    
    # 定义时间段的名称映射
    def get_time_period(hour):
        if 0 <= hour < 6:
            return "凌晨"
        elif 6 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        else:  # 18 <= hour < 24
            return "晚上"
    
    # 获取目标时间的格式化时间
    formatted_time = f"{target_time.hour}:{target_time.minute:02d}:{target_time.second:02d}"
    time_period = get_time_period(target_time.hour)
    
    # 刚刚（一分钟内）
    if time_diff < 60:
        return "刚刚"
    
    # x分钟前（一小时内）
    elif time_diff < 3600:
        minutes = int(time_diff // 60)
        return f"{minutes}分钟前"
    
    # x小时前（当天内）
    elif current_time.date() == target_time.date():
        hours = int(time_diff // 3600)
        return f"{hours}小时前"
    
    # 昨天/前天 + 时间段 + 具体时间
    elif (current_time.date() - target_time.date()).days <= 2:
        day_str = "昨天" if (current_time.date() - target_time.date()).days == 1 else "前天"
        return f"{day_str} {time_period} {formatted_time}"
    
    # 本周/上周 + 星期几 + 时间段 + 具体时间
    elif (current_time.date() - target_time.date()).days <= 14:
        # 获取星期几
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday = weekdays[target_time.weekday()]
        
        # 判断是本周还是上周
        target_week_num = target_time.isocalendar()[1]
        current_week_num = current_time.isocalendar()[1]
        
        if target_week_num == current_week_num:
            week_str = "本周"
        elif target_week_num == current_week_num - 1:
            week_str = "上周"
        else:
            # 不是上周，按日期显示
            return f"{target_time.month}月{target_time.day}日 {time_period} {formatted_time}"
        
        return f"{week_str}{weekday} {time_period} {formatted_time}"
    
    # 今年的日期 + 时间段 + 具体时间
    elif current_time.year == target_time.year:
        return f"{target_time.month}月{target_time.day}日 {time_period} {formatted_time}"
    
    # 完整日期 + 时间段 + 具体时间
    else:
        return f"{target_time.year}年{target_time.month}月{target_time.day}日 {time_period} {formatted_time}"
    
def safe_sample(lst, num):
    """
    从列表中进行不重复抽样，如果请求的样本数量超过列表长度，则返回整个列表。
    
    :param lst: 原始列表
    :param num: 请求的样本数量
    :return: 抽样后的列表或原始列表
    """
    if num > len(lst):
        return lst
    else:
        return random.sample(lst, num)

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