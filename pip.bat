python -m venv venv
call venv\Scripts\activate
@echo off
echo 正在安装Python依赖库...
echo 若遇权限问题，请以管理员身份运行此脚本！

pip install ^
jieba ^
flask ^
flask-cors ^
waitress ^
beautifulsoup4 ^
