import os

def write_llbot_config(role, send_port, listen_port):
    content = """
{
  "webui": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 3080
  },
  "milky": {
    "enable": false,
    "reportSelfMessage": false,
    "http": {
      "host": "127.0.0.1",
      "port": 3010,
      "prefix": "",
      "accessToken": ""
    },
    "webhook": {
      "urls": [],
      "accessToken": ""
    }
  },
  "satori": {
    "enable": false,
    "host": "127.0.0.1",
    "port": 5600,
    "token": ""
  },
  "ob11": {
    "enable": true,
    "connect": [
      {
        "type": "ws",
        "enable": false,
        "host": "127.0.0.1",
        "port": 3001,
        "heartInterval": 60000,
        "token": "",
        "reportSelfMessage": false,
        "reportOfflineMessage": false,
        "messageFormat": "array",
        "debug": false
      },
      {
        "type": "ws-reverse",
        "enable": false,
        "url": "",
        "heartInterval": 60000,
        "token": "",
        "reportSelfMessage": false,
        "reportOfflineMessage": false,
        "messageFormat": "array",
        "debug": false
      },
      {
        "type": "http",
        "enable": true,
        "host": "127.0.0.1",
        "port": %s,
        "token": "",
        "reportSelfMessage": false,
        "reportOfflineMessage": false,
        "messageFormat": "array",
        "debug": true
      },
      {
        "type": "http-post",
        "enable": true,
        "url": "http://127.0.0.1:%s",
        "enableHeart": false,
        "heartInterval": 60000,
        "token": "",
        "reportSelfMessage": false,
        "reportOfflineMessage": false,
        "messageFormat": "array",
        "debug": false
      }
    ]
  },
  "enableLocalFile2Url": false,
  "log": true,
  "autoDeleteFile": false,
  "autoDeleteFileSecond": 60,
  "musicSignUrl": "https://ss.xingzhige.com/music_card/card",
  "msgCacheExpire": 120,
  "ffmpeg": "",
  "rawMsgPB": false
}"""%(str(send_port), str(listen_port))
    if not os.path.exists(f"tools/llonebot/bin/llbot/data"):
        os.makedirs(f"tools/llonebot/bin/llbot/data")
    with open(f"tools/llonebot/bin/llbot/data/config_{role}.json", "w", encoding="utf-8") as f:
        f.write(content)