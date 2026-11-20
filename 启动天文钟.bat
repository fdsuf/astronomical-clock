@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem 优先启动打包好的 exe（GUI 子系统，绝不闪 cmd 窗口）
set "EXE=%~dp0dist\桌面天文机械表.exe"
if exist "%EXE%" (
    start "" "%EXE%"
    exit /b
)

rem 没有 exe 时回退到源码运行；必须用 pythonw.exe，用 python.exe 会闪一下 cmd 窗口
set "PYW=C:\Users\dell\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe"
if exist "%PYW%" (
    start "" "%PYW%" "%~dp0astronomical_clock.py"
    exit /b
)

start "" pythonw "%~dp0astronomical_clock.py"
