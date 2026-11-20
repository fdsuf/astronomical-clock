# -*- coding: utf-8 -*-
"""桌面天文机械表 —— 双击启动入口（无 cmd 窗口）。

为什么要这个文件：
    Windows 把 .py 关联到 python.exe（控制台程序），双击会先闪一个黑窗口。
    .pyw 关联到 pythonw.exe（GUI 子系统），双击不会出现任何控制台窗口。
    此文件只负责把主程序跑起来，所有逻辑仍在 astronomical_clock.py。

推荐用法：
    日常使用请直接双击 dist\\桌面天文机械表.exe（已打包，无需 Python 环境）。
    本文件用于改了源码后想立刻看效果、又不想看到黑窗口的场景。
"""
import os
import runpy
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

# 以 __main__ 身份执行主程序，等价于直接运行 astronomical_clock.py
runpy.run_path(os.path.join(_HERE, "astronomical_clock.py"), run_name="__main__")
