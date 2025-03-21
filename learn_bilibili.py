import requests
import requests
import re
import random
import os
import time

url = 'https://www.bilibili.com/video/%s/'%random.choice(["BV1Z5DpYbE4r","BV1AC4y1P743","BV1f1mRY2EGZ","BV1bVB1YLEom","BV1Gb42177YX","BV17m411U77c","BV16KU7YkETb","BV1MzDmYJE2c"])
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def post(BV):                  #发生请求，获取html
    BVurl = 'https://www.bilibili.com/video/%s/'%BV
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(BVurl, headers=headers)
    html_content = response.text
    return html_content

def extract_BV(html_content):#提取BV号
    try:
        if "slide_ad" in html_content:      # 有订阅合集内容的视频
            keyword = "slide_ad"
            pattern = f"{keyword}(.*?)px;\">"
            match = re.search(pattern, html_content)
            result = match.group(1)
            keyword1 = "href=\"/video/BV"
            pattern1 = f"{keyword1}(.*?)?sp"
            match1 = re.search(pattern1, result)
            result1 = match1.group(1)
            result1="BV"+result1.replace("/?","")
            print(result1)
            return result1
    except:
        if "class=\"video-page-card-small\"" in html_content:  # 没有订阅合集内容的视频
            keyword = "class=\"video-page-card-small\""
            pattern = f"{keyword}(.*?)px;\">"
            match = re.search(pattern, html_content)
            result = match.group(1)
            keyword1 = "href=\"/video/BV"
            pattern1 = f"{keyword1}(.*?)/?sp"
            match1 = re.search(pattern1, result)
            result1 = match1.group(1)
            result1 = "BV" + result1.replace("/?", "")
            print(result1)
            return result1

def get_video_msg(new_html_content):
    if "data-title" in new_html_content:
        try:
            keyword = "data-title=\""
            pattern = f"{keyword}(.*?)\""
            match = re.search(pattern, new_html_content)
            title = match.group(1)
            keyword1 = "data-v-181fa804>"
            pattern1 = f"{keyword1}(.*?)</span>"
            match1 = re.search(pattern1, new_html_content)
            result1 = match1.group(1)
            return title, result1.replace("<span class=\"desc-info-text\" data-v-181fa804>","")
        except:
            try:
                keyword = "data-title=\""
                pattern = f"{keyword}(.*?)\""
                match = re.search(pattern, new_html_content)
                title = match.group(1)
                keyword1 = "\"desc_v2\":[{\"raw_text\":\""
                pattern1 = f"{keyword1}(.*?)\",\"type\""
                match1 = re.search(pattern1, new_html_content)
                result1 = match1.group(1)
                return title, result1
            except:
                keyword = "data-title=\""
                pattern = f"{keyword}(.*?)\""
                match = re.search(pattern, new_html_content)
                title = match.group(1)
                print("视频内容介绍获取失败")
                return title,"视频内容介绍获取失败"

def circulation(new_html_content):
    global num
    BV = extract_BV(new_html_content)
    new_html_content = post(BV)
    video_msg = get_video_msg(new_html_content)
    # print(new_html_content)
    timestamp = time.time()
    localtime = time.localtime(timestamp)
    current_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", localtime
    )
    try:
        print("[%s]视频标题:%s" % (current_time, video_msg[0]))
        print("视频信息:%s" % video_msg[1])
        if "视频内容介绍获取失败" in video_msg or len(video_msg[1]) > 50:
          video_msg=video_msg[0]
          with open(
                    "./user/lb_content.txt",
                    "w",
                    encoding="utf-8",
            ) as txt:
                txt.write("[%s]视频标题:%s" %(current_time,video_msg.replace("视频内容介绍获取失败",""))+"。\n\n")
        if "视频内容介绍获取失败" not in video_msg or len(video_msg[1]) < 50:
            with open(
                    "./user/lb_content.txt",
                    "w",
                    encoding="utf-8",
            ) as txt:
                txt.write("[%s]视频标题:%s" % (current_time, video_msg) + "\n" + "视频信息:%s" % video_msg[1] + "。\n\n")
    except:
        print("视频获取失败")
    time.sleep(3)
    return new_html_content

aa=True
def LB_main():
    global aa
    global num
    if aa==True:
        response = requests.get(url, headers=headers)
        html_content = response.text
        BV=extract_BV(html_content)
        new_html_content=post(BV)
        video_msg=get_video_msg(new_html_content)
        # print(new_html_content)
        # try:
        #     print("视频标题:%s" % video_msg[0])
        #     print("视频信息:%s" % video_msg[1])
        #     if "视频内容介绍获取失败" in video_msg[1] or len(video_msg[1])>30:
        #         video_msg=video_msg[1][1]+"..."
        #     with open(
        #             "./user/lb_content.txt",
        #             "a",
        #             encoding="utf-8",
        #     ) as txt:
        #         txt.write("%d视频标题:%s" %(num,video_msg[0]) + "\n" + "视频信息:%s" % video_msg[1] + "。\n\n")
        #     num+=1
        # except:
        #     print("视频获取失败")
        # max_iterations = 2  # 限制循环次数
        # for _ in range(max_iterations):
        #     new_html_content = circulation(new_html_content)

LB_main()
"""
知道beautifulsoup就是不用，就是玩，豪赤的史要与大家一起分享
"""