from flask import Flask, Response, request, jsonify, send_from_directory
from flask_cors import CORS
from waitress import serve
import os

app = Flask(__name__)
CORS(app)


@app.route('/data/image/<filename>', methods=['GET', 'POST'])
def image_files(filename):
    print("用户请求文件：",filename)
    if os.path.exists(os.path.join('./data/image/', filename)):
        # 发送文件作为响应
        return send_from_directory('./data/image/', filename, as_attachment=True)
    else:
        # 文件不存在时返回404错误
        return 'File not found', 404
@app.route('/data/voice/<filename>', methods=['GET', 'POST'])
def voice_files(filename):
    print("用户请求文件：",filename)
    if os.path.exists(os.path.join('./data/voice/', filename)):
        # 发送文件作为响应
        return send_from_directory('./data/voice/', filename, as_attachment=True)
    else:
        # 文件不存在时返回404错误
        return 'File not found', 404

serve(app, host='127.0.0.1', port=4321, threads=10)