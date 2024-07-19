import socket
import json
 
 
 
ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(('127.0.0.1', 3001))
ListenSocket.listen(100)
 
HttpResponseHeader = '''HTTP/1.1 200 OK
Content-Type: text/html
'''
 
def request_to_json(msg):
    dicstrmsg=msg.split("\r\n\r\n")[-1]
    return json.loads(dicstrmsg)
    for i in range(len(dicstrmsg)):
        if msg[i]=="{" and msg[-1]=="\n":
            return json.loads(msg[i:])
    return None
 
# 需要循环执行，返回值为json格式
def rev_msg():# json or None
    Client, Address = ListenSocket.accept()
    Request = Client.recv(10240).decode(encoding='utf-8')
    rev_json=request_to_json(Request)
    Client.sendall((HttpResponseHeader).encode(encoding='utf-8'))
    Client.close()
    return rev_json