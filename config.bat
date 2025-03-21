@echo off
REM 获取脚本所在目录
set "script_dir=%~dp0"
REM 去除末尾反斜杠（可选）
set "script_dir=%script_dir:~0,-1%"

echo 正在处理目录：%script_dir%
dir "%script_dir%"
python "%dir%GUI.py"

exit