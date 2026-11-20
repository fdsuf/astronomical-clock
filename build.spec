# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：桌面天文机械表

关键点：
  console=False     —— 打包为窗口程序（GUI 子系统），双击不会闪出黑色 cmd 窗口
  onefile           —— 单文件 exe，便于分发
  icon              —— 程序图标 app.ico（含 16~256 多尺寸，任务栏/资源管理器都清晰）
  excludes          —— 排除用不到的重型库，显著减小体积

构建：pyinstaller build.spec --noconfirm
产物：dist/桌面天文机械表.exe
"""
import os

import sys

block_cipher = None

APP_NAME = "桌面天文机械表"
ENTRY = "astronomical_clock.py"

a = Analysis(
    [ENTRY],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # PyQt6 里本程序完全没用到的模块（含 QtWebEngine 体积巨大）
        "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineQuick",
        "PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.QtQuickWidgets", "PyQt6.QtQuick3D",
        "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets", "PyQt6.QtBluetooth",
        "PyQt6.QtNfc", "PyQt6.QtPositioning", "PyQt6.QtSensors", "PyQt6.QtSerialPort",
        "PyQt6.QtSql", "PyQt6.QtTest", "PyQt6.QtDesigner", "PyQt6.QtHelp",
        "PyQt6.QtOpenGL", "PyQt6.QtOpenGLWidgets", "PyQt6.QtPdf", "PyQt6.QtPdfWidgets",
        "PyQt6.QtSvg", "PyQt6.QtSvgWidgets", "PyQt6.QtCharts", "PyQt6.QtDataVisualization",
        "PyQt6.QtNetworkAuth", "PyQt6.QtRemoteObjects", "PyQt6.QtScxml",
        "PyQt6.QtSpatialAudio", "PyQt6.QtStateMachine", "PyQt6.QtTextToSpeech",
        "PyQt6.QtWebChannel", "PyQt6.QtWebSockets", "PyQt6.QtXml",
        # 科学计算栈（本程序只用标准库 math）
        "numpy", "pandas", "scipy", "matplotlib", "PIL", "PyQt5", "tkinter",
        "setuptools", "pydoc", "doctest", "unittest", "test",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,              # 不用 UPX：偶发被杀软误报，且对 PyQt 压缩收益有限
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # ← 关键：不弹 cmd 窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="app.ico",
)
