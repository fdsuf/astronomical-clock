# -*- coding: utf-8 -*-
"""
桌面天文机械表 - 挂机版
Python + PyQt6 单文件实现
天文算法：Meeus 简化算法（太阳视黄经 / 月相 / 恒星时 / 二十四节气）
六种样式：经典天文钟 / 赛博朋克霓虹 / 极简现代 / 中式古风 / 高仿真机械表 / 天文机械腕表
"""
import sys
import os
import math
import json
import random
import urllib.request
from datetime import datetime, timezone

from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QLineF, QSettings, QThread, pyqtSignal, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QPainterPath, QIcon,
    QFontMetrics, QFontMetricsF, QPixmap, QConicalGradient, QLinearGradient, QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QInputDialog, QMessageBox, QSystemTrayIcon,
)

# ---------------- 配色 ----------------
BRASS        = QColor(186, 117, 23)
BRASS_DARK   = QColor(133, 79, 11)
BRASS_LIGHT  = QColor(239, 159, 39)
BRASS_PALE   = QColor(250, 238, 218)
STAR_BG      = QColor(10, 24, 48, 235)
STAR_DEEP    = QColor(4, 28, 83)
STAR_BLUE    = QColor(24, 95, 165)
STAR_LIGHT   = QColor(181, 212, 244)
MOON_DARK    = QColor(26, 42, 66)
MOON_LIT     = QColor(245, 230, 200)
NEEDLE_H     = QColor(133, 79, 11)
NEEDLE_M     = QColor(245, 230, 200)
NEEDLE_S     = QColor(163, 45, 45)
TEXT_DARK    = QColor(66, 40, 8)
WHITE        = QColor(255, 255, 255)

# 赛博朋克配色
CYBER_BG     = QColor(8, 8, 13, 240)
CYBER_CYAN   = QColor(0, 240, 255)
CYBER_PINK   = QColor(255, 45, 149)
CYBER_DIM    = QColor(120, 200, 210)

# 极简配色
MINI_BG      = QColor(255, 255, 255, 245)
MINI_INK     = QColor(44, 44, 42)
MINI_GRAY    = QColor(200, 200, 198)
MINI_RED     = QColor(226, 75, 74)

# 中式配色
HAN_BG       = QColor(245, 238, 220, 245)
HAN_INK      = QColor(44, 44, 42)
HAN_RED      = QColor(185, 58, 43)
HAN_GOLD     = QColor(160, 130, 60)

# 高仿真机械表配色（炭灰机芯 / 玫瑰金 / 钢色 / 红宝石）
MECH_BG      = QColor(28, 29, 33, 250)     # 表盘深底
MECH_PLATE   = QColor(44, 46, 52)          # 机芯板
MECH_PLATE2  = QColor(58, 61, 68)          # 机芯板亮面
MECH_STRIPE  = QColor(52, 55, 62)          # 日内瓦纹
MECH_STEEL   = QColor(184, 188, 194)       # 拉丝钢
MECH_STEEL_D = QColor(110, 116, 124)       # 暗钢
MECH_STEEL_L = QColor(226, 231, 236)       # 亮钢
MECH_ROSE    = QColor(190, 138, 92)        # 玫瑰金齿轮
MECH_ROSE_D  = QColor(120, 82, 50)         # 暗玫瑰金
MECH_RUBY    = QColor(179, 18, 43)         # 红宝石轴承
MECH_BLUE    = QColor(38, 70, 130)         # 蓝钢指针
MECH_BLUE_L  = QColor(90, 125, 190)        # 蓝钢高光
MECH_TEXT    = QColor(232, 228, 218)       # 米白刻度文字

# 天文机械腕表配色（深蓝珐琅 / 银钢 / 玫瑰金 / 蓝钢 / 红宝石）
ASTRO_ENAMEL  = QColor(20, 40, 70)          # 深蓝珐琅盘
ASTRO_ENAMEL_D = QColor(11, 26, 50)         # 珐琅深影
ASTRO_STEEL   = QColor(198, 205, 214)       # 银钢
ASTRO_STEEL_D = QColor(108, 118, 132)       # 暗钢
ASTRO_STEEL_L = QColor(244, 248, 252)       # 亮钢高光
ASTRO_ROSE    = QColor(206, 158, 104)       # 玫瑰金
ASTRO_ROSE_D  = QColor(132, 88, 48)         # 暗玫瑰金
ASTRO_ROSE_L  = QColor(246, 214, 166)       # 玫瑰金高光
ASTRO_RUBY    = QColor(179, 18, 43)         # 红宝石
ASTRO_BLUE    = QColor(38, 72, 140)         # 蓝钢
ASTRO_BLUE_L  = QColor(110, 150, 215)       # 蓝钢高光
ASTRO_GOLD    = QColor(224, 190, 112)       # 金色天文指示
ASTRO_MOON    = QColor(247, 235, 205)       # 月面
ASTRO_TEXT    = QColor(232, 224, 206)       # 米白文字

THEMES = ["classic", "cyber", "minimal", "chinese", "mechanical", "astro"]
THEME_NAMES = {
    "classic": "经典天文钟",
    "cyber": "赛博朋克霓虹",
    "minimal": "极简现代",
    "chinese": "中式古风",
    "mechanical": "高仿真机械表",
    "astro": "天文机械腕表",
}
SIZES = [280, 340, 400, 500, 600]
BASE = 400.0  # 逻辑绘制基准边长

# 托盘图标配色（按主题取一对「盘面底色 / 指针·边框色」，保证 16px 下仍可辨认）
TRAY_PALETTE = {
    "classic":    (QColor(26, 20, 12), QColor(239, 176, 92)),
    "cyber":      (QColor(10, 10, 16), QColor(0, 240, 255)),
    "minimal":    (QColor(250, 250, 248), QColor(44, 44, 42)),
    "chinese":    (QColor(245, 238, 220), QColor(185, 58, 43)),
    "mechanical": (QColor(26, 28, 32), QColor(214, 158, 96)),
    "astro":      (QColor(10, 24, 48), QColor(216, 178, 118)),
}
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== 齿轮系：统一模数 + 节圆相切 + 齿数比联动 + 相位咬合 =====
GEAR_MODULE = 1.25                      # 模数 m：所有齿轮齿高一致，是啮合的前提
# 传动链（节圆半径 = m*齿数/2）。每条边从上一个节点按 dir 方向摆放，中心距=两节圆半径和
# 结构：条盒轮→中心轮→三轮→四轮→擒纵轮；条盒轮与三轮都直接啮合中心轮（真实轮系拓扑）
GEAR_TRAIN = [
    # name,      teeth, parent,  dir(度, 相对 parent)
    ("barrel",   52,  None,    None),      # 条盒轮（主动，最慢）
    ("center",   32,  "barrel", 45.0),     # 中心轮（在条盒右下，与条盒啮合）
    ("third",    24,  "center", -20.0),    # 三轮（中心轮右上）
    ("fourth",   20,  "third",  92.0),     # 四轮（三轮下方）
    ("escape",   15,  "fourth", 130.0),    # 擒纵轮（四轮左下）
    # —— 自动上链轮系分支（同样由条盒轮带动，节圆相切、相位咬合）——
    ("ratchet",  22,  "barrel", 195.0),    # 棘轮（条盒左侧）
    ("crown",    14,  "ratchet", 265.0),   # 皇冠轮（立轮，棘轮上方）
    ("auto",     18,  "crown",  330.0),    # 自动轮（皇冠轮右上）
]

# 自动陀（摆陀）：半圆配重 + 内齿圈，绕盘心缓慢旋转；内齿圈与 auto 轮真实内啮合。
# 内齿圈半径 R = 中心→auto 距离 + auto节圆半径；齿数 z = 2R/m（取最接近整数）。
ROTOR_TEETH = 186
ROTOR_MARGIN = 0.5      # 内啮合齿槽对齐微调（齿比例，渲染验证用）

# 陀飞轮：以擒纵轮轴为框架中心，擒纵叉 + 摆轮整体随框架绕轴公转（1 圈/分钟）。
# 擒纵轮本身保持固定轴心，继续与四轮严格啮合；叉的瓦臂始终指向擒纵轮（保持咬合）。
TOURB_PERIOD = 60.0             # 框架公转周期（秒/圈）
TOURB_FORK_R = 17.0             # 框架中心→叉轴 距离（= 原 L_fe，保证瓦臂搭上擒纵轮）
TOURB_SLOT = 14.0               # 叉口到圆盘钉距离
TOURB_PIN_R = 7.0               # 圆盘钉回转半径
TOURB_BAL_R = 24.0              # 摆轮半径（缩小以容纳于框架内）
TOURB_CAGE_R = 63.0             # 框架外半径

# 副盘位置与尺寸
MOON_SUB = (265.0, 135.0)       # 月相副盘（右上）
RESERVE_SUB = (135.0, 270.0)    # 动力储存副盘（左下）
# 日期/节气盘避开中心轮系：DATE 沿左下移到条盒轮与陀飞轮框架之间的空白桥板，
# TERM 沿右上移到陀飞轮框架之外。两盘半径均约 96，与原两盘对称。
DATE_SUB = (107.0, 221.5)       # 星期日期副盘（左中偏下）
TERM_SUB = (294.0, 180.0)       # 二十四节气副盘（右中偏上）
SUB_R = 20.0                    # 副盘半径
WEEK_CN = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")  # weekday() 0=周一


def _gear_radius(teeth):
    """节圆半径（模数统一）"""
    return GEAR_MODULE * teeth / 2.0


def _mesh_angle(alpha, n_from, n_to, phi_from):
    """外啮合从动轮相位（度）。
    alpha: 主动轮中心 → 从动轮中心 的方向角（度）。
    保证主动轮的齿顶对准从动轮的齿槽（像拉链咬合），且转速 = -主动轮转速 * n_from/n_to。
    推导：齿顶中心在齿序 k+0.26、齿槽中心在 k+0.76（和为 1.02≈1）。
    令 ui=(alpha-φi)*ni/360、uj=(alpha+180-φj)*nj/360，啮合不变量 ui+uj≡0 (mod 1)。
    解出 φj = alpha + 180 + (ni/nj)*(alpha - φi)。
    """
    return alpha + 180.0 + (n_from / n_to) * (alpha - phi_from)

J2000 = 2451545.0
DAYS_PER_YEAR = 365.25


def _make_star_points():
    """预生成星盘星点（固定种子，相对坐标），避免每帧重复计算随机数"""
    rng = random.Random(20240101)
    pts = []
    for _ in range(70):
        ang = rng.uniform(0, 2 * math.pi)
        rad = math.sqrt(rng.random())
        size = 1.0 + rng.random() * 1.6
        pts.append((ang, rad, size))
    return pts


STAR_POINTS = _make_star_points()

# ---------------- 天文算法（Meeus 简化） ----------------

def julian_day(dt_utc):
    y, m = dt_utc.year, dt_utc.month
    d = (dt_utc.day + dt_utc.hour / 24.0 + dt_utc.minute / 1440.0
         + dt_utc.second / 86400.0)
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def sun_apparent_longitude(jd):
    n = jd - J2000
    L = (280.460 + 0.9856474 * n) % 360.0
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
    return lam % 360.0


def moon_longitude(jd):
    n = jd - J2000
    Lp = math.radians((218.316 + 13.176396 * n) % 360.0)
    Mp = math.radians((134.963 + 13.064993 * n) % 360.0)
    lam = 218.316 + 13.176396 * n + 6.289 * math.sin(Mp)
    F = math.radians((93.272 + 13.229350 * n) % 360.0)
    lam += 1.274 * math.sin(2 * (Lp - math.radians(sun_apparent_longitude(jd))) - Mp)
    lam -= 0.214 * math.sin(2 * F)
    return lam % 360.0


def moon_elongation(jd):
    return (moon_longitude(jd) - sun_apparent_longitude(jd)) % 360.0


def gmst_degrees(jd):
    t = (jd - J2000) / DAYS_PER_YEAR
    gmst = 280.46061837 + 360.98564736629 * (jd - J2000)
    gmst += 0.000387933 * t * t - t * t * t / 38710000.0
    return gmst % 360.0


def local_sidereal_degrees(jd, longitude_east):
    return (gmst_degrees(jd) + longitude_east) % 360.0


SOLAR_TERMS = [
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
]
ZODIACS = [
    "白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
    "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼",
]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def _make_mech_patterns():
    """预生成机械表所需的固定纹理点：罗马纹放射线、日内瓦纹、太阳纹、摆轮游丝"""
    rng = random.Random(19940321)
    sunburst = [rng.uniform(-0.5, 0.5) for _ in range(240)]          # 表盘放射拉丝微扰
    geneva = list(range(-270, 75, 7))  # 机芯斜纹的横向偏移 ox
    hairspring = []
    for i in range(121):
        f = i / 120.0
        ang = f * math.pi * 2 * 3.3
        rad = 2.0 + f * 22.0
        hairspring.append((rad * math.cos(ang), rad * math.sin(ang)))
    return sunburst, geneva, hairspring


MECH_SUNBURST, MECH_GENEVA, MECH_HAIRSPRING = _make_mech_patterns()


def solar_term_info(sun_lon):
    idx = int(sun_lon // 15.0) % 24
    progress = (sun_lon % 15.0) / 15.0
    return SOLAR_TERMS[idx], progress


# ---------------- IP 定位 ----------------
class Locator(QThread):
    located = pyqtSignal(float, float)

    def run(self):
        lat, lon = 30.0, 120.0
        try:
            url = "http://ip-api.com/json/?fields=status,lat,lon"
            req = urllib.request.Request(url, headers={"User-Agent": "AstroClock/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8", "ignore"))
                if data.get("status") == "success":
                    lat = float(data["lat"])
                    lon = float(data["lon"])
        except Exception:
            pass
        self.located.emit(lat, lon)


# ---------------- 主窗口 ----------------
class AstroClock(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AstroClock", "AstroClock")
        self.lat = float(self.settings.value("lat", 30.0))
        self.lon = float(self.settings.value("lon", 120.0))
        self.topmost = bool(self.settings.value("topmost", True))
        self.theme = self.settings.value("theme", "classic")
        if self.theme not in THEMES:
            self.theme = "classic"
        self.size_px = int(self.settings.value("size_px", 400))
        if self.size_px not in SIZES:
            self.size_px = 400
        self.drag_pos = QPoint()
        self.resizing = False
        self.resize_start = QPoint()
        self.resize_start_size = self.size_px

        self.setWindowTitle("桌面天文机械表")
        self._apply_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(self.size_px, self.size_px)

        saved_pos = self.settings.value("pos")
        if saved_pos is not None:
            self.move(saved_pos)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(screen.right() - self.size_px - 10, screen.top() + 20)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

        self.font_cn = QFont("Microsoft YaHei", 9)
        self.font_num = QFont("Segoe UI", 9)
        self.font_small = QFont("Segoe UI", 8)
        self.font_big = QFont("Consolas", 30)
        self.font_big.setBold(True)
        self.font_roman = QFont("Georgia", 15)
        self.font_roman.setBold(True)
        self.font_roman_s = QFont("Georgia", 10)
        self.font_roman_out = QFont("Georgia", 13)  # 外圈罗马数字时标（醒目）
        self.font_roman_out.setBold(True)
        self.font_sub = QFont("Georgia", 8)   # 副盘小标签
        self.font_sub.setBold(True)
        self.font_sub_cn = QFont("Microsoft YaHei", 5)  # 副盘内中文（节气/星期）
        self.font_sub_cn.setBold(True)
        self.mech_static = None  # 机械表静态层缓存（表壳/刻度/机芯板）
        self.astro_static = None  # 天文腕表静态层缓存
        self.rotor_pm = None     # 自动陀旋转体缓存（齿圈+配重，只旋转贴图）
        self.rotor_half = 0.0
        self.tourb_pm = None     # 陀飞轮框架缓存（桥板+外圈+螺钉，只旋转贴图）
        self.tourb_half = 0.0

        # 首次交互预热相关：把字体字形/静态贴图/右键菜单的一次性初始化提前到启动阶段
        self._ctx = None         # 天文数据缓存（每秒算一次，不必每帧重算）
        self._ctx_sec = -1
        self._menu = None        # 右键菜单对象缓存（避免每次重建）
        self._menu_acts = {}     # 菜单 action 引用，便于刷新勾选标记

        self.locator = Locator()
        self.locator.located.connect(self.on_located)
        self.locator.start()

        # 托盘图标：左键单击 显示/隐藏，右键弹出与表盘一致的菜单
        self._tray_minute = -1
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self._make_tray_icon())
        self._update_tray_tip()
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.setVisible(True)

        # 每分钟刷新一次托盘图标与提示（图标上的指针要跟着走，但不必每帧重画）
        self.tray_timer = QTimer(self)
        self.tray_timer.timeout.connect(self._refresh_tray)
        self.tray_timer.start(15000)

        # 启动后空闲预热：消化首次右键/拖动的一次性初始化开销
        QTimer.singleShot(300, self._warm_up)

    def _apply_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.topmost:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    # ---- 托盘图标 ----
    def _make_tray_icon(self):
        """生成托盘图标：圆形小表盘 + 时/分针 + 12 格刻度。
        以 2x 超采样再交给 Qt 缩放，保证 16px 下仍清晰（直接画大表盘细节会糊成一团）。"""
        dpr = 2
        S = 64
        pm = QPixmap(S * dpr, S * dpr)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.scale(dpr, dpr)
        bg, accent = TRAY_PALETTE.get(self.theme, TRAY_PALETTE["mechanical"])
        c = S / 2.0
        r = c - 2.0

        # 盘面
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bg))
        p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))
        # 浅色盘面在浅色任务栏上会失去轮廓，补一圈半透明深色描边保证可见性
        if bg.lightness() > 140:
            p.setPen(QPen(QColor(60, 60, 60, 190), 1.4))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))
        # 外圈
        p.setPen(QPen(accent, 2.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))
        # 12 格刻度（只画整点，5 格足够小尺寸辨认）
        for k in range(12):
            a = math.radians(k * 30.0 - 90.0)
            r1 = r - 4.5
            r2 = r - 1.8
            p.setPen(QPen(accent, 1.6 if k % 3 == 0 else 1.0))
            p.drawLine(QLineF(c + r1 * math.cos(a), c + r1 * math.sin(a),
                              c + r2 * math.cos(a), c + r2 * math.sin(a)))

        now = datetime.now()
        hour_a = math.radians((now.hour % 12 + now.minute / 60.0) * 30.0 - 90.0)
        min_a = math.radians(now.minute * 6.0 - 90.0)
        # 分针
        pen = QPen(accent, 2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(c, c, c + (r - 5.0) * math.cos(min_a),
                          c + (r - 5.0) * math.sin(min_a)))
        # 时针（更粗更短）
        pen = QPen(accent, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(c, c, c + (r - 12.0) * math.cos(hour_a),
                          c + (r - 12.0) * math.sin(hour_a)))
        # 中心轴
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(accent))
        p.drawEllipse(QRectF(c - 2.0, c - 2.0, 4.0, 4.0))
        p.end()
        return QIcon(pm)

    def _update_tray_tip(self):
        try:
            now = datetime.now()
            state = "已隐藏" if not self.isVisible() else "显示中"
            self.tray.setToolTip(
                "桌面天文机械表 · %s\n%s  %s\n左键单击显示/隐藏，右键更多设置"
                % (now.strftime("%H:%M"), THEME_NAMES.get(self.theme, ""), state))
        except (RuntimeError, AttributeError):
            pass  # 退出过程中托盘对象可能已销毁

    def _refresh_tray(self):
        """每分钟更新一次图标指针与提示（分钟数变化时才重画，省开销）。"""
        now = datetime.now()
        if now.minute != self._tray_minute:
            self._tray_minute = now.minute
            self.tray.setIcon(self._make_tray_icon())
        self._update_tray_tip()

    def _on_tray_activated(self, reason):
        """托盘左键单击 → 显示/隐藏窗口。双击由两次单击组成，故只处理 Trigger。"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visible()

    def toggle_visible(self):
        """在显示 / 隐藏之间切换。"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            if self.topmost:
                self.raise_()
                self.activateWindow()
            self.update()
        self._update_tray_tip()
        if self._menu is not None:
            self._refresh_menu()

    def on_located(self, lat, lon):
        self.lat, self.lon = lat, lon
        self.settings.setValue("lat", lat)
        self.settings.setValue("lon", lon)

    # ---- 交互 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            handle = int(18 * self.width() / BASE)
            if pos.x() >= self.width() - handle and pos.y() >= self.height() - handle:
                self.resizing = True
                self.resize_start = event.globalPosition().toPoint()
                self.resize_start_size = self.width()
            else:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.resizing:
                delta = event.globalPosition().toPoint() - self.resize_start
                new_size = max(220, min(900, max(self.resize_start_size + delta.x(),
                                                 self.resize_start_size + delta.y())))
                self.resize(new_size, new_size)
            else:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            self.size_px = self.width()
            self.settings.setValue("size_px", self.size_px)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self.toggle_topmost()

    def closeEvent(self, event):
        self.settings.setValue("pos", self.pos())
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        if getattr(self, "tray", None) is not None:
            self._update_tray_tip()
            if self._menu is not None:
                self._refresh_menu()

    def hideEvent(self, event):
        super().hideEvent(event)
        if getattr(self, "tray", None) is not None:
            self._update_tray_tip()
            if self._menu is not None:
                self._refresh_menu()

    def _build_menu(self):
        """构建右键菜单一次并缓存。托盘图标右键与表盘右键共用同一个菜单对象，
        行为完全一致。菜单/子菜单/字体设置在启动时完成，
        避免首次右键时因创建原生菜单 + 首次加载中文字体而卡顿。
        顶层动作统一走 menu.triggered → _on_menu_action，
        这样无论是 exec() 弹出还是托盘原生弹出都能正确处理。"""
        menu = QMenu(self)
        menu.setFont(self.font_cn)

        style_menu = menu.addMenu("表盘样式")
        style_menu.setFont(self.font_cn)
        acts = []
        for key in THEMES:
            act = style_menu.addAction(THEME_NAMES[key])
            act.setData(key)
            acts.append(act)
        style_menu.triggered.connect(lambda a: self.set_theme(a.data()))
        self._menu_acts["styles"] = (acts, style_menu)

        size_menu = menu.addMenu("尺寸")
        size_menu.setFont(self.font_cn)
        sacts = []
        for sz in SIZES:
            act = size_menu.addAction("%d × %d" % (sz, sz))
            act.setData(sz)
            sacts.append(act)
        size_menu.triggered.connect(lambda a: self.set_size(a.data()))
        self._menu_acts["sizes"] = (sacts, size_menu)

        menu.addSeparator()
        self._menu_acts["top"] = menu.addAction("窗口置顶")
        self._menu_acts["top"].setCheckable(True)
        self._menu_acts["vis"] = menu.addAction("隐藏窗口")
        self._menu_acts["loc"] = menu.addAction("设置经纬度…")
        self._menu_acts["about"] = menu.addAction("关于")
        menu.addSeparator()
        self._menu_acts["quit"] = menu.addAction("退出")

        menu.triggered.connect(self._on_menu_action)
        # 托盘原生弹出菜单时不会走 contextMenuEvent，故用 aboutToShow 统一刷新
        menu.aboutToShow.connect(self._refresh_menu)
        return menu

    def _on_menu_action(self, act):
        """菜单动作统一入口（表盘右键 / 托盘右键 共用）。"""
        if act is self._menu_acts.get("top"):
            self.toggle_topmost()
        elif act is self._menu_acts.get("vis"):
            self.toggle_visible()
        elif act is self._menu_acts.get("loc"):
            self.set_location()
        elif act is self._menu_acts.get("about"):
            self._dialog_about()
        elif act is self._menu_acts.get("quit"):
            self._quit()

    def _refresh_menu(self):
        """刷新菜单勾选标记与动态文案（菜单对象复用，不重建）。
        状态一变就调用，保证「表盘右键」与「托盘右键」看到的勾选永远一致。"""
        acts_styles = self._menu_acts.get("styles")
        if not acts_styles:
            return  # 菜单尚未构建
        style_acts = acts_styles[0]
        for act, key in zip(style_acts, THEMES):
            act.setText(THEME_NAMES[key] + ("  ✓" if key == self.theme else ""))
        for act, sz in zip(self._menu_acts["sizes"][0], SIZES):
            act.setText("%d × %d" % (sz, sz) + ("  ✓" if sz == self.size_px else ""))
        self._menu_acts["top"].setChecked(self.topmost)
        self._menu_acts["vis"].setText("隐藏窗口" if self.isVisible() else "显示窗口")

    def contextMenuEvent(self, event):
        """表盘右键：与托盘右键同一套菜单。"""
        if self._menu is None:
            self._menu = self._build_menu()
        self._refresh_menu()
        self._menu.exec(event.globalPos())

    def _quit(self):
        """退出：先撤掉托盘图标，否则残留图标会留在通知区直到鼠标划过。"""
        self.settings.setValue("pos", self.pos())
        self.tray.setVisible(False)
        QApplication.quit()

    def _warm_up(self):
        """启动后预热一次性开销：中文字形缓存 + 平台菜单样式 + 静态贴图。
        在事件循环空闲时调用，让首次右键/拖动不再卡顿。"""
        # 1) 触发中文/数字字形缓存：离屏绘制所有菜单会用到的字符串
        warm = QPixmap(64, 64)
        warm.fill(QColor(0, 0, 0, 0))
        wp = QPainter(warm)
        wp.setFont(self.font_cn)
        strings = ["表盘样式", "尺寸", "窗口置顶", "隐藏窗口", "设置经纬度…", "关于", "退出"] + \
                  list(THEME_NAMES.values()) + \
                  ["%d × %d" % (s, s) for s in SIZES]
        for s in strings:
            wp.drawText(QRectF(0, 0, 64, 64), int(Qt.AlignmentFlag.AlignLeft), s)
        wp.end()
        # 2) 预构建菜单并做一次 show/hide，完成 Qt 平台原生菜单样式初始化
        #    （不能用 exec()，那是模态阻塞；show/hide 同样会触发原生窗口创建）
        if self._menu is None:
            self._menu = self._build_menu()
        self._refresh_menu()
        self._menu.show()
        self._menu.hide()
        # 2b) 托盘右键菜单挂上与表盘完全相同的菜单对象
        self.tray.setContextMenu(self._menu)
        # 3) 预构建当前主题的静态贴图（避免首次绘制时构建导致卡顿）
        if self.theme == "mechanical" and self.mech_static is None:
            self.mech_static = self._build_mech_static()
        elif self.theme == "astro" and self.astro_static is None:
            self.astro_static = self._build_astro_static()
        # 4) 预热拖动路径：触发 frameGeometry() 首次查询 + 让 DWM 为半透明窗口
        #    建立合成资源（微小位移后复位，用户无感知）
        self.frameGeometry()
        p = self.pos()
        self.move(p + QPoint(1, 1))
        self.move(p)

    def _suspend_topmost(self):
        """打开对话框前临时取消置顶，返回是否原本置顶"""
        was = self.topmost
        if was:
            pos = self.pos()
            self.topmost = False
            self._apply_flags()
            self.show()
            self.move(pos)
        return was

    def _restore_topmost(self, was):
        if was:
            pos = self.pos()
            self.topmost = True
            self._apply_flags()
            self.show()
            self.move(pos)

    def _dialog_about(self):
        was = self._suspend_topmost()
        try:
            QMessageBox.information(
                self, "关于",
                "桌面天文机械表\n\n"
                "六种样式：经典天文钟 / 赛博朋克霓虹 / 极简现代 / 中式古风 / 高仿真机械表 / 天文机械腕表\n"
                "当前样式：%s\n"
                "天文算法：Meeus 简化算法，离线计算\n"
                "当前位置：北纬 %.2f° 东经 %.2f°\n\n"
                "拖动移动 · 右下角拖拽缩放 · 双击切置顶 · 右键菜单"
                % (THEME_NAMES[self.theme], self.lat, self.lon),
            )
        finally:
            self._restore_topmost(was)

    def set_theme(self, key):
        if key in THEMES:
            self.theme = key
            self.settings.setValue("theme", key)
            if getattr(self, "tray", None) is not None:
                self.tray.setIcon(self._make_tray_icon())
                self._update_tray_tip()
            if self._menu is not None:
                self._refresh_menu()
            self.update()

    def set_size(self, sz):
        if sz in SIZES:
            self.size_px = sz
            pos = self.pos()
            self.resize(sz, sz)
            self.settings.setValue("size_px", sz)
            self.move(pos)
            if self._menu is not None:
                self._refresh_menu()

    def toggle_topmost(self):
        self.topmost = not self.topmost
        pos = self.pos()
        self._apply_flags()
        self.show()
        self.move(pos)
        self.settings.setValue("topmost", self.topmost)
        if getattr(self, "tray", None) is not None:
            self._update_tray_tip()
        if self._menu is not None:
            self._refresh_menu()

    def set_location(self):
        was = self._suspend_topmost()
        try:
            lat, ok1 = QInputDialog.getDouble(
                self, "设置纬度", "北纬（度）:", self.lat, -90.0, 90.0, 2)
            if not ok1:
                return
            lon, ok2 = QInputDialog.getDouble(
                self, "设置经度", "东经（度）:", self.lon, -180.0, 180.0, 2)
            if not ok2:
                return
            self.lat, self.lon = lat, lon
            self.settings.setValue("lat", lat)
            self.settings.setValue("lon", lon)
        finally:
            self._restore_topmost(was)

    # ---- 绘制入口 ----
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        s = self.width() / BASE
        p.scale(s, s)

        # 天文数据每秒算一次即可（太阳/月亮/恒星时在一秒内变化极小）；
        # local 时间每帧更新，保证扫动秒针顺滑。避免每帧重算降低交互响应。
        now = datetime.now()
        sec_key = int(now.timestamp())
        if self._ctx is None or sec_key != self._ctx_sec:
            self._ctx_sec = sec_key
            now_utc = datetime.now(timezone.utc)
            jd = julian_day(now_utc)
            sun_lon = sun_apparent_longitude(jd)
            term, term_prog = solar_term_info(sun_lon)
            # 太阳赤纬与昼长：驱动外圈「昼夜弧」的亮/暗分段（用当时纬度）
            dec = math.degrees(math.asin(math.sin(math.radians(23.4397))
                                         * math.sin(math.radians(sun_lon))))
            cos_h = -math.tan(math.radians(max(-89.0, min(89.0, self.lat)))) \
                * math.tan(math.radians(dec))
            cos_h = max(-1.0, min(1.0, cos_h))
            day_len = 2.0 * math.degrees(math.acos(cos_h)) / 15.0
            self._ctx = {
                "jd": jd,
                "sun_lon": sun_lon,
                "elong": moon_elongation(jd),
                "lst": local_sidereal_degrees(jd, self.lon),
                "term": term,
                "term_prog": term_prog,
                "zodiac_idx": int(sun_lon // 30.0) % 12,
                "sun_dec": dec,
                "day_len": day_len,
                "sunrise": 12.0 - day_len / 2.0,
                "sunset": 12.0 + day_len / 2.0,
            }
        ctx = self._ctx
        ctx["local"] = now
        painter_for = {
            "classic": self.paint_classic,
            "cyber": self.paint_cyber,
            "minimal": self.paint_minimal,
            "chinese": self.paint_chinese,
            "mechanical": self.paint_mechanical,
            "astro": self.paint_astro,
        }
        painter_for[self.theme](p, ctx)
        self.draw_resize_handle(p)
        p.end()

    def draw_resize_handle(self, p):
        x, y = 388.0, 388.0
        p.setPen(QPen(QColor(120, 120, 120, 160), 1))
        for i in range(3):
            off = i * 4
            p.drawLine(QLineF(x - off, y + 6, x + 6, y - off))

    # ================= 样式 1：经典天文钟 =================
    def paint_classic(self, p, ctx):
        cx = cy = 200.0
        self.draw_case(p, cx, cy)
        self.draw_zodiac(p, cx, cy, ctx["sun_lon"], ctx["zodiac_idx"])
        self.draw_hour_ring(p, cx, cy)
        self.draw_star_chart(p, cx, cy, ctx["lst"], ctx["jd"])
        self.draw_moon(p, cx, cy, ctx["elong"])
        self.draw_term(p, cx, cy, ctx["term"], ctx["term_prog"])
        self.draw_gears(p, cx, cy, ctx["local"], ctx["jd"], ctx["elong"], ctx["lst"])
        self.draw_hands(p, cx, cy, ctx["local"])

    def draw_case(self, p, cx, cy):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(STAR_BG))
        p.drawEllipse(QRectF(cx - 196, cy - 196, 392, 392))
        p.setPen(QPen(BRASS, 2.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - 195, cy - 195, 390, 390))
        p.setPen(QPen(BRASS_DARK, 1))
        p.drawEllipse(QRectF(cx - 188, cy - 188, 376, 376))

    def draw_zodiac(self, p, cx, cy, sun_lon, active_idx):
        r_out, r_in = 188.0, 162.0
        p.setBrush(QBrush(BRASS_PALE))
        p.setPen(QPen(BRASS, 1.2))
        p.drawEllipse(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out))
        p.setBrush(QBrush(STAR_DEEP))
        p.drawEllipse(QRectF(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in))
        for i, name in enumerate(ZODIACS):
            a0 = math.radians(i * 30 - 90 - 15)
            a1 = math.radians(i * 30 - 90 + 15)
            am = math.radians(i * 30 - 90)
            path = QPainterPath()
            path.moveTo(cx + r_in * math.cos(a0), cy + r_in * math.sin(a0))
            path.arcTo(QRectF(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in), i * 30 - 105, 30)
            path.lineTo(cx + r_out * math.cos(a1), cy + r_out * math.sin(a1))
            path.arcTo(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out), i * 30 - 75, -30)
            path.closeSubpath()
            p.setBrush(QBrush(BRASS_LIGHT if i == active_idx else BRASS_PALE))
            p.setPen(QPen(BRASS_DARK, 0.6))
            p.drawPath(path)
            p.setFont(self.font_cn)
            p.setPen(QPen(TEXT_DARK if i == active_idx else BRASS_DARK))
            tx = cx + (r_in + r_out) / 2 * math.cos(am)
            ty = cy + (r_in + r_out) / 2 * math.sin(am)
            p.drawText(QRectF(tx - 18, ty - 9, 36, 18), Qt.AlignmentFlag.AlignCenter, name)
        p.setPen(QPen(BRASS_DARK, 0.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out))

    def draw_hour_ring(self, p, cx, cy):
        r_out, r_in = 160.0, 148.0
        p.setBrush(QBrush(STAR_DEEP))
        p.setPen(QPen(BRASS, 1))
        p.drawEllipse(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out))
        for i in range(60):
            a = math.radians(i * 6 - 90)
            major = (i % 5 == 0)
            r1 = r_in - (10 if major else 4)
            p.setPen(QPen(BRASS_LIGHT if major else BRASS, 1.6 if major else 0.7))
            p.drawLine(QLineF(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                              cx + (r_in - 1) * math.cos(a), cy + (r_in - 1) * math.sin(a)))
        for h in range(1, 13):
            a = math.radians(h * 30 - 90)
            p.setFont(self.font_num)
            p.setPen(QPen(WHITE))
            x = cx + 135 * math.cos(a)
            y = cy + 135 * math.sin(a)
            p.drawText(QRectF(x - 12, y - 10, 24, 20), Qt.AlignmentFlag.AlignCenter, str(h))

    def draw_star_chart(self, p, cx, cy, lst, jd):
        r = 100.0
        p.setBrush(QBrush(STAR_DEEP))
        p.setPen(QPen(BRASS, 1))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.save()
        p.translate(cx, cy)
        p.rotate(lst)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(STAR_LIGHT))
        for ang, rad_norm, size in STAR_POINTS:
            rad = rad_norm * (r - 8)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            p.drawEllipse(QRectF(x - size, y - size, 2 * size, 2 * size))
        p.setPen(QPen(BRASS_LIGHT, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-4, -4, 8, 8))
        p.restore()
        p.setFont(self.font_small)
        p.setPen(QPen(STAR_LIGHT))
        p.drawText(QRectF(cx - 40, cy + r - 16, 80, 14),
                   Qt.AlignmentFlag.AlignCenter, "恒星时 %.1f°" % lst)

    def draw_moon(self, p, cx, cy, elong):
        r = 46.0
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(MOON_DARK))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        waxing = elong < 180.0
        c = math.cos(math.radians(elong))
        steps = 80
        pts = []
        for i in range(steps + 1):
            y = -r + 2 * r * i / steps
            w = math.sqrt(max(0.0, r * r - y * y))
            x0, x1 = (c * w, w) if waxing else (-w, -c * w)
            pts.append((cx + x0, cy + y))
        for i in range(steps, -1, -1):
            y = -r + 2 * r * i / steps
            w = math.sqrt(max(0.0, r * r - y * y))
            x0, x1 = (c * w, w) if waxing else (-w, -c * w)
            pts.append((cx + x1, cy + y))
        p.setBrush(QBrush(MOON_LIT))
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
        illum = (1 - math.cos(math.radians(elong))) / 2.0
        p.setPen(QPen(BRASS_LIGHT, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setFont(self.font_small)
        p.setPen(QPen(BRASS_PALE))
        p.drawText(QRectF(cx - 50, cy + r + 2, 100, 14),
                   Qt.AlignmentFlag.AlignCenter, "月面 %.0f%%" % (illum * 100))

    def draw_term(self, p, cx, cy, term, progress):
        r = 62.0
        p.setPen(QPen(BRASS, 0.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.setPen(QPen(BRASS_LIGHT, 3))
        p.drawArc(QRectF(cx - r, cy - r, 2 * r, 2 * r), int(-90 * 16), int(-360 * progress * 16))
        p.setFont(self.font_cn)
        p.setPen(QPen(BRASS_PALE))
        p.drawText(QRectF(cx - 30, cy - r - 13, 60, 14), Qt.AlignmentFlag.AlignCenter, term)

    def draw_gears(self, p, cx, cy, local, jd, elong, lst):
        gears = [
            (cx - 26, cy - 20, 14, 10, -(local.second * 6.0)),
            (cx + 26, cy - 20, 14, 10, (local.second * 6.0)),
            (cx, cy + 26, 18, 12, (local.hour * 30 + local.minute * 0.5)),
        ]
        for gx, gy, r, teeth, ang in gears:
            self.draw_gear(p, gx, gy, r, teeth, ang)

    def draw_gear(self, p, gx, gy, r, teeth, angle_deg):
        pts = []
        for i in range(teeth * 2):
            a = math.radians(angle_deg + i * 180.0 / teeth)
            rr = r if i % 2 == 0 else r * 0.82
            pts.append((gx + rr * math.cos(a), gy + rr * math.sin(a)))
        p.setPen(QPen(BRASS_DARK, 0.8))
        p.setBrush(QBrush(BRASS))
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
        p.setBrush(QBrush(STAR_DEEP))
        p.drawEllipse(QRectF(gx - r * 0.35, gy - r * 0.35, r * 0.7, r * 0.7))

    def draw_hands(self, p, cx, cy, local):
        def hand(angle_deg, length, pen, back=12):
            a = math.radians(angle_deg - 90)
            p.setPen(pen)
            p.drawLine(QLineF(cx - back * math.cos(a), cy - back * math.sin(a),
                              cx + length * math.cos(a), cy + length * math.sin(a)))
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0
        pen_h = QPen(NEEDLE_H); pen_h.setWidth(5); pen_h.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_m = QPen(NEEDLE_M); pen_m.setWidth(3); pen_m.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_s = QPen(NEEDLE_S); pen_s.setWidthF(1.6); pen_s.setCapStyle(Qt.PenCapStyle.RoundCap)
        hand(hour * 30, 92, pen_h)
        hand(minute * 6, 128, pen_m)
        hand(sec * 6, 140, pen_s)
        p.setPen(QPen(BRASS_DARK, 1))
        p.setBrush(QBrush(BRASS_LIGHT))
        p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))

    # ================= 样式 2：赛博朋克霓虹 =================
    def paint_cyber(self, p, ctx):
        cx = cy = 200.0
        local = ctx["local"]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(CYBER_BG))
        p.drawEllipse(QRectF(cx - 196, cy - 196, 392, 392))

        # 霓虹外环
        p.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(CYBER_CYAN, 2.2); pen.setWidthF(2.2)
        p.setPen(pen)
        p.drawEllipse(QRectF(cx - 188, cy - 188, 376, 376))
        pen2 = QPen(CYBER_PINK, 1.2); pen2.setWidthF(1.2)
        p.setPen(pen2)
        p.drawEllipse(QRectF(cx - 158, cy - 158, 316, 316))
        p.setPen(QPen(CYBER_CYAN, 0.5))
        p.drawEllipse(QRectF(cx - 128, cy - 128, 256, 256))

        # 刻度
        for i in range(60):
            a = math.radians(i * 6 - 90)
            major = (i % 5 == 0)
            r1 = 158 if major else 166
            col = CYBER_PINK if major else CYBER_CYAN
            p.setPen(QPen(col, 1.6 if major else 0.8))
            p.drawLine(QLineF(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                              cx + 176 * math.cos(a), cy + 176 * math.sin(a)))

        # 扫描线
        p.setPen(QPen(CYBER_CYAN, 0.5))
        for yy in range(-120, 121, 24):
            p.drawLine(QLineF(cx - 120, cy + yy, cx + 120, cy + yy))

        # 数字时间
        t = local.strftime("%H:%M:%S")
        p.setFont(self.font_big)
        p.setPen(QPen(CYBER_CYAN))
        p.drawText(QRectF(cx - 110, cy - 42, 220, 60), Qt.AlignmentFlag.AlignCenter, t)
        p.setFont(self.font_num)
        p.setPen(QPen(CYBER_PINK))
        p.drawText(QRectF(cx - 110, cy + 20, 220, 20), Qt.AlignmentFlag.AlignCenter,
                   local.strftime("%Y.%m.%d"))
        p.setFont(self.font_cn)
        p.setPen(QPen(CYBER_DIM))
        p.drawText(QRectF(cx - 110, cy + 46, 220, 20), Qt.AlignmentFlag.AlignCenter,
                   "节气 %s · %s座" % (ctx["term"], ZODIACS[ctx["zodiac_idx"]]))

        # 霓虹指针
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0
        pen_h = QPen(CYBER_PINK, 3); pen_h.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_m = QPen(CYBER_CYAN, 2); pen_m.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_s = QPen(WHITE, 1); pen_s.setCapStyle(Qt.PenCapStyle.RoundCap)
        for ang, ln, pen in [(hour * 30, 80, pen_h), (minute * 6, 108, pen_m), (sec * 6, 120, pen_s)]:
            a = math.radians(ang - 90)
            p.setPen(pen)
            p.drawLine(QLineF(cx - 14 * math.cos(a), cy - 14 * math.sin(a),
                              cx + ln * math.cos(a), cy + ln * math.sin(a)))
        p.setPen(QPen(CYBER_CYAN, 1))
        p.setBrush(QBrush(CYBER_BG))
        p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))

        p.setFont(self.font_small)
        p.setPen(QPen(CYBER_DIM))
        p.drawText(QRectF(cx - 90, cy + 150, 180, 16), Qt.AlignmentFlag.AlignCenter,
                   "SYS // 恒星时 %.1f°" % ctx["lst"])

    # ================= 样式 3：极简现代 =================
    def paint_minimal(self, p, ctx):
        cx = cy = 200.0
        local = ctx["local"]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(MINI_BG))
        p.drawEllipse(QRectF(cx - 192, cy - 192, 384, 384))

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(MINI_GRAY, 1))
        p.drawEllipse(QRectF(cx - 184, cy - 184, 368, 368))
        p.setPen(QPen(MINI_INK, 0.8))
        p.drawEllipse(QRectF(cx - 168, cy - 168, 336, 336))

        # 极简 12 刻度
        for i in range(12):
            a = math.radians(i * 30 - 90)
            p.setPen(QPen(MINI_INK, 1))
            p.drawLine(QLineF(cx + 156 * math.cos(a), cy + 156 * math.sin(a),
                              cx + 166 * math.cos(a), cy + 166 * math.sin(a)))
        # 12点红点
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(MINI_RED))
        p.drawEllipse(QRectF(cx - 3, cy - 172, 6, 6))

        # 细指针
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0
        pen_h = QPen(MINI_INK, 3); pen_h.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_m = QPen(MINI_INK, 2); pen_m.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_s = QPen(MINI_RED, 1); pen_s.setCapStyle(Qt.PenCapStyle.RoundCap)
        for ang, ln, pen in [(hour * 30, 88, pen_h), (minute * 6, 126, pen_m), (sec * 6, 140, pen_s)]:
            a = math.radians(ang - 90)
            p.setPen(pen)
            p.drawLine(QLineF(cx, cy, cx + ln * math.cos(a), cy + ln * math.sin(a)))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(MINI_INK))
        p.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))

        # 顶部小时数字
        p.setFont(QFont("Segoe UI Light", 13))
        p.setPen(QPen(MINI_INK))
        p.drawText(QRectF(cx - 60, cy - 130, 120, 24), Qt.AlignmentFlag.AlignCenter,
                   local.strftime("%H:%M"))
        # 底部：节气 + 月相小副盘
        p.setFont(self.font_cn)
        p.setPen(QPen(MINI_INK))
        p.drawText(QRectF(cx - 60, cy + 100, 120, 20), Qt.AlignmentFlag.AlignCenter, ctx["term"])
        # 月相小圆
        mr = 16
        mcx, mcy = cx, cy + 142
        p.setPen(QPen(MINI_GRAY, 0.8))
        p.setBrush(QBrush(WHITE))
        p.drawEllipse(QRectF(mcx - mr, mcy - mr, 2 * mr, 2 * mr))
        illum = (1 - math.cos(math.radians(ctx["elong"]))) / 2.0
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(MINI_INK))
        p.drawChord(QRectF(mcx - mr, mcy - mr, 2 * mr, 2 * mr), 90 * 16, int(360 * illum * 16))
        p.setFont(self.font_small)
        p.setPen(QPen(MINI_INK))
        p.drawText(QRectF(cx + 24, mcy - 9, 60, 18), Qt.AlignmentFlag.AlignLeft,
                   "月 %.0f%%" % (illum * 100))

    # ================= 样式 4：中式古风 =================
    def paint_chinese(self, p, ctx):
        cx = cy = 200.0
        local = ctx["local"]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(HAN_BG))
        p.drawEllipse(QRectF(cx - 192, cy - 192, 384, 384))

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(HAN_INK, 2))
        p.drawEllipse(QRectF(cx - 186, cy - 186, 372, 372))
        p.setPen(QPen(HAN_RED, 1.2))
        p.drawEllipse(QRectF(cx - 176, cy - 176, 352, 352))
        p.setPen(QPen(HAN_GOLD, 0.8))
        p.drawEllipse(QRectF(cx - 150, cy - 150, 300, 300))

        # 十二地支
        font_han = QFont("SimSun", 13)
        for i, name in enumerate(EARTHLY_BRANCHES):
            a = math.radians(i * 30 - 90)
            tx = cx + 163 * math.cos(a)
            ty = cy + 163 * math.sin(a)
            p.setFont(font_han)
            p.setPen(QPen(HAN_RED))
            p.drawText(QRectF(tx - 13, ty - 12, 26, 24), Qt.AlignmentFlag.AlignCenter, name)

        # 中心太极
        tr = 46.0
        p.setPen(QPen(HAN_INK, 1))
        p.setBrush(QBrush(HAN_BG))
        p.drawEllipse(QRectF(cx - tr, cy - tr, 2 * tr, 2 * tr))
        path = QPainterPath()
        path.moveTo(cx, cy - tr)
        path.arcTo(QRectF(cx - tr, cy - tr, 2 * tr, 2 * tr), 270, -180)
        path.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(HAN_INK))
        p.drawPath(path)
        p.setBrush(QBrush(HAN_INK))
        p.drawEllipse(QRectF(cx - tr / 2 - tr / 5, cy - tr / 2 - tr / 5, tr * 0.4, tr * 0.4))
        p.setBrush(QBrush(HAN_BG))
        p.drawEllipse(QRectF(cx + tr / 2 - tr / 5, cy + tr / 2 - tr / 5, tr * 0.4, tr * 0.4))
        p.setBrush(QBrush(HAN_BG))
        p.drawEllipse(QRectF(cx - tr / 2 - 3, cy - tr / 2 - 3, 6, 6))
        p.setBrush(QBrush(HAN_INK))
        p.drawEllipse(QRectF(cx + tr / 2 - 3, cy + tr / 2 - 3, 6, 6))

        # 节气 + 时辰
        p.setFont(QFont("SimSun", 12))
        p.setPen(QPen(HAN_RED))
        p.drawText(QRectF(cx - 60, cy - 132, 120, 22), Qt.AlignmentFlag.AlignCenter, "节气 · " + ctx["term"])
        hour_branch = EARTHLY_BRANCHES[((local.hour + 1) // 2) % 12]
        p.drawText(QRectF(cx - 60, cy + 112, 120, 22), Qt.AlignmentFlag.AlignCenter,
                   "时辰 · " + hour_branch)
        p.setFont(QFont("SimSun", 10))
        p.setPen(QPen(HAN_INK))
        p.drawText(QRectF(cx - 70, cy + 150, 140, 18), Qt.AlignmentFlag.AlignCenter,
                   "%s  %02d:%02d" % (local.strftime("%Y年%m月%d日"), local.hour, local.minute))

        # 朱砂指针
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0
        pen_h = QPen(HAN_INK, 3); pen_h.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_m = QPen(HAN_RED, 2); pen_m.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_s = QPen(HAN_GOLD, 1); pen_s.setCapStyle(Qt.PenCapStyle.RoundCap)
        for ang, ln, pen in [(hour * 30, 86, pen_h), (minute * 6, 122, pen_m), (sec * 6, 136, pen_s)]:
            a = math.radians(ang - 90)
            p.setPen(pen)
            p.drawLine(QLineF(cx - 12 * math.cos(a), cy - 12 * math.sin(a),
                              cx + ln * math.cos(a), cy + ln * math.sin(a)))


    # ================= 样式 5：高仿真机械表 =================
    # ================= 样式 5：高仿真机械表（独立零件 · 联动机芯）=================
    def _build_mech_static(self):
        """静态机芯底：表壳 / 太阳纹盘 / 桥板 / 罗马时标 / 螺丝 / 文字（2x 缓存）"""
        dpr = 2
        pm = QPixmap(int(BASE * dpr), int(BASE * dpr))
        pm.fill(QColor(0, 0, 0, 0))
        sp = QPainter(pm)
        sp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        sp.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        sp.scale(dpr, dpr)
        cx = cy = 200.0
        self.mm_case(sp, cx, cy)
        self.mm_dial(sp, cx, cy)
        self.mm_bridges(sp, cx, cy)
        self.mm_chapter(sp, cx, cy)
        self.mm_screws(sp, cx, cy)
        sp.end()
        return pm

    def _mech_gear_layout(self):
        """按 GEAR_TRAIN 计算各齿轮位置（节圆相切）与摆轮/擒纵叉位置。
        返回 (pos, teeth)，pos[name]=(x,y)。中心轮固定在盘心。"""
        teeth = {name: n for name, n, _, _ in GEAR_TRAIN}
        rad = {name: _gear_radius(n) for name, n in teeth.items()}
        pos = {}
        for name, n, parent, direction in GEAR_TRAIN:
            if parent is None:
                pos[name] = (0.0, 0.0)
            else:
                a = math.radians(direction)
                px, py = pos[parent]
                dist = rad[parent] + rad[name]          # 节圆相切 → 真正啮合
                pos[name] = (px + dist * math.cos(a), py + dist * math.sin(a))
        # 整体平移，使中心轮落在表盘几何中心
        ox = 200.0 - pos["center"][0]
        oy = 200.0 - pos["center"][1]
        pos = {k: (x + ox, y + oy) for k, (x, y) in pos.items()}
        return pos, teeth, rad

    def paint_mechanical(self, p, ctx):
        """独立零件 + 严格啮合轮系：节圆相切、齿数比联动、相位咬合、游丝呼吸。"""
        cx = cy = 200.0
        local = ctx["local"]
        t = local.timestamp()

        pos, teeth, rad = self._mech_gear_layout()

        # ---- 统一驱动相位：整条轮系由条盒轮单一角速度带动，逐级按齿数比反向啮合 ----
        # 注意：相位不能取模！条盒轮每 8.8s 转一圈，若 %360 会在环绕处让下游
        # 齿轮（尤其自动陀内齿圈）产生 ~100° 跳变，表现为"外框转一半就复位"。
        # 累积角直接随时间线性增长，由 QPainter.rotate / cos 自动归一化。
        barrel_phi = t * 41.0                      # 条盒轮主动，转速最慢（约 8.8s/圈）
        phi = {"barrel": barrel_phi}
        for name, n, parent, direction in GEAR_TRAIN:
            if parent is not None:
                # direction 即 父中心→子中心 的方向角 alpha
                phi[name] = _mesh_angle(direction, teeth[parent], teeth[name], phi[parent])

        # ===== 陀飞轮：框架绕擒纵轮轴整体公转（1 圈/分钟），叉 + 摆轮随框架同步旋转 =====
        # 擒纵轮保持在固定轴心，继续与四轮严格啮合；叉的瓦臂由角度公式自动始终指向擒纵轮，
        # 因此框架转到任意角度，摆轮→圆盘钉→叉→擒纵轮 这条咬合链都不脱开。
        cage_ang = (t / TOURB_PERIOD) * 360.0        # 框架公转角（连续累加，不取模）
        theta_c = math.radians(cage_ang)
        ex, ey = pos["escape"]                       # 框架中心 = 擒纵轮轴

        f_bal = 2.0                                  # 摆轮 2Hz 简谐摆动（相对框架）
        phase = t * 2.0 * math.pi * f_bal
        s = math.sin(phase)
        osc_ang = s * 30.0                           # 摆轮相对框架的振荡角
        bal_ang = cage_ang + osc_ang                 # 摆轮绝对转角 = 公转 + 振荡

        base_dir = math.radians(150.0)               # 框架 0° 时 E→叉→摆轮 的排布方向
        ux, uy = math.cos(base_dir + theta_c), math.sin(base_dir + theta_c)
        L_fe, L_slot, pin_r = TOURB_FORK_R, TOURB_SLOT, TOURB_PIN_R
        fork_pos = (ex + ux * L_fe, ey + uy * L_fe)
        bal_pos = (ex + ux * (L_fe + L_slot + pin_r), ey + uy * (L_fe + L_slot + pin_r))
        bal_r = TOURB_BAL_R
        # 圆盘钉在摆轮局部的固定角：指向叉轴（= 150° + 180°）。随摆轮/框架一起转。
        pin_base = 330.0
        pa = math.radians(pin_base + bal_ang)
        pin = (bal_pos[0] + pin_r * math.cos(pa), bal_pos[1] + pin_r * math.sin(pa))
        # 擒纵叉转角：叉口咬住圆盘钉；其瓦臂(+y)自动指向框架中心的擒纵轮，全程保持咬合
        fork_ang = math.degrees(math.atan2(pin[1] - fork_pos[1], pin[0] - fork_pos[0])) + 90.0

        # ===== 自动陀：半圆配重 + 内齿圈，绕盘心摆动；内齿圈与 auto 轮内啮合 =====
        # 内啮合相位（大齿圈包住小齿轮，同向）：φ_ring = α + (z_auto/z_ring)·(φ_auto - α) + 180/z_ring
        # 其中 α 为 盘心→auto 轮 的方向角；auto 相位来自上面已算好的轮系。
        auto_x, auto_y = pos["auto"]
        alpha_ra = math.degrees(math.atan2(auto_y - cy, auto_x - cx))
        rotor_ang = alpha_ra + (teeth["auto"] / ROTOR_TEETH) * (phi["auto"] - alpha_ra) \
                    + 180.0 / ROTOR_TEETH
        # 注：摆陀相位严格由内啮合决定（不叠加自由摆角），否则齿会脱开——咬合优先。

        # 1) 静态机芯底（表壳/盘面/桥板/时标，缓存贴图）
        if self.mech_static is None:
            self.mech_static = self._build_mech_static()
        p.drawPixmap(QRectF(0, 0, BASE, BASE), self.mech_static,
                     QRectF(0, 0, self.mech_static.width(), self.mech_static.height()))

        # 1b) 外圈动态效果：秒点流光 / 昼夜弧 / 表壳光泽 / 年度进度环
        #     四项均在 r>160 的无零件区，齿轮最外仅到 r≈116，故此刻绘制不会被遮挡
        self.mm_outer_fx(p, cx, cy, ctx, local)

        # 1c) 自动陀（镂空半圆配重 + 内齿圈）：压在最底层，所有轮系与陀飞轮都盖在它之上，
        #     避免摆陀的大块配重遮住轮系；内齿圈与 auto 轮仍是真实内啮合。
        self.mm_rotor(p, cx, cy, rotor_ang)

        # 2) 活动零件：严格啮合的轮系（自后向前绘制，轴心宝石压在齿上）
        self.mm_barrel(p, *pos["barrel"], rad["barrel"], phi["barrel"])
        # 自动上链轮系分支：棘轮 → 皇冠轮 → 自动轮（与主链共用模数/相位引擎，全部严格咬合）
        self.mm_ratchet(p, *pos["ratchet"], rad["ratchet"], teeth["ratchet"], phi["ratchet"])
        self.mm_gear(p, *pos["crown"], rad["crown"], teeth["crown"], phi["crown"], MECH_STEEL)
        self.mm_gear(p, *pos["auto"], rad["auto"], teeth["auto"], phi["auto"], MECH_ROSE)
        # 走时主轮系
        self.mm_gear(p, *pos["center"], rad["center"], teeth["center"], phi["center"], MECH_ROSE)
        self.mm_gear(p, *pos["third"], rad["third"], teeth["third"], phi["third"], MECH_STEEL)
        self.mm_gear(p, *pos["fourth"], rad["fourth"], teeth["fourth"], phi["fourth"], MECH_ROSE)

        # 2c) 陀飞轮框架（桥板/外圈，绕擒纵轮轴整体旋转）
        self.mm_tourbillon(p, *pos["escape"], cage_ang)
        self.mm_escape_wheel(p, *pos["escape"], rad["escape"], phi["escape"])
        self.mm_pallet_fork(p, *fork_pos, fork_ang, L_slot, frame_ang=cage_ang)
        # 擒纵锁放瞬间火花（叉瓦刚锁定/释放擒纵轮齿时）
        self.mm_escape_spark(p, *fork_pos, fork_ang, s)
        self.mm_balance(p, *bal_pos, bal_r, bal_ang, s, pin, pin_base,
                        pin_r=pin_r, frame_ang=cage_ang)

        # 3) 动态光影：金属反光扫带 + 宝石高光呼吸
        self.mm_light_sweep(p, cx, cy, t)
        # 3b) 副盘：月相 + 动力储存 + 星期日期 + 二十四节气（四象限对称）
        self.mm_moon_subdial(p, *MOON_SUB, ctx["elong"])
        self.mm_power_subdial(p, *RESERVE_SUB, t)
        self.mm_date_subdial(p, *DATE_SUB, local)
        self.mm_term_subdial(p, *TERM_SUB, ctx["term"], ctx["term_prog"])
        # 4) 指针（扫动秒针）
        self.mm_hands(p, cx, cy, local)
        # 5) 机芯铭牌文字：画在最顶层，不被齿轮/指针遮挡（配合深色底衬）
        self.mm_text(p, cx, cy)

    # ---------- 独立零件绘制 ----------
    def mm_case(self, p, cx, cy):
        """拉丝钢表壳：锥形渐变金属反光 + 玫瑰金倒角 + 圆润珠状滚花"""
        p.setPen(Qt.PenStyle.NoPen)
        g = QConicalGradient(cx, cy, 55)
        for pos, col in [(0.0, "#eef2f6"), (0.12, "#828a95"), (0.26, "#d5dce4"),
                         (0.40, "#4c535e"), (0.52, "#e6ebf1"), (0.66, "#6d7581"),
                         (0.80, "#d0d8e0"), (0.90, "#545c67"), (1.0, "#eef2f6")]:
            g.setColorAt(pos, QColor(col))
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(cx - 196, cy - 196, 392, 392))

        # 外缘圆润倒角：径向暗化过渡，让最外圈有厚度感而非硬切边
        bevel = QRadialGradient(cx, cy, 196)
        bevel.setColorAt(0.90, QColor(10, 12, 16, 0))
        bevel.setColorAt(0.965, QColor(10, 12, 16, 55))
        bevel.setColorAt(1.0, QColor(6, 8, 12, 130))
        p.setBrush(QBrush(bevel))
        p.drawEllipse(QRectF(cx - 196, cy - 196, 392, 392))

        # 滚花：圆头短刻线（末端半圆，不再是尖硬的锯齿轮廓），长度缩短、对比柔化
        for i in range(180):
            a = math.radians(i * 2)
            c = QColor(MECH_STEEL_L if i % 2 == 0 else MECH_STEEL_D)
            c.setAlpha(165)
            pen = QPen(c, 0.9)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(cx + 191.5 * math.cos(a), cy + 191.5 * math.sin(a),
                              cx + 195.0 * math.cos(a), cy + 195.0 * math.sin(a)))

        # 玫瑰金倒角环
        g2 = QConicalGradient(cx, cy, 140)
        for pos, col in [(0.0, "#f2caa2"), (0.30, "#8a5b35"), (0.55, "#e3b083"),
                         (0.80, "#6e4325"), (1.0, "#f2caa2")]:
            g2.setColorAt(pos, QColor(col))
        p.setBrush(QBrush(g2))
        p.drawEllipse(QRectF(cx - 187, cy - 187, 374, 374))
        # 银→金过渡柔化：内缘一圈半透明高光环
        p.setPen(QPen(QColor(255, 255, 255, 45), 1.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - 186, cy - 186, 372, 372))
        # 盘面深底
        p.setBrush(QBrush(MECH_BG))
        p.drawEllipse(QRectF(cx - 181, cy - 181, 362, 362))

    def mm_dial(self, p, cx, cy):
        """太阳放射纹盘底 + 中心渐变暗角"""
        r = 181.0
        clip = QPainterPath()
        clip.addEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.save()
        p.setClipPath(clip)
        for i, _ in enumerate(MECH_SUNBURST):
            a = math.radians(i * 1.5)
            col = MECH_PLATE2 if (i % 7 == 0) else MECH_PLATE
            p.setPen(QPen(col, 0.8))
            p.drawLine(QLineF(cx + 18 * math.cos(a), cy + 18 * math.sin(a),
                              cx + r * math.cos(a), cy + r * math.sin(a)))
        # 中心柔光
        g = QRadialGradient(cx, cy, r)
        g.setColorAt(0.0, QColor(70, 74, 82, 90))
        g.setColorAt(0.6, QColor(40, 42, 48, 30))
        g.setColorAt(1.0, QColor(10, 10, 12, 120))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        # 同心车纹（机芯装饰圈）
        p.setPen(QPen(QColor(118, 124, 134, 70), 0.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        for rr in (48, 82, 108, 132):
            p.drawEllipse(QRectF(cx - rr, cy - rr, 2 * rr, 2 * rr))
        p.restore()

    def mm_bridges(self, p, cx, cy):
        """机芯桥板：日内瓦斜纹底板 + 两块倒角钢桥"""
        r = 150.0
        clip = QPainterPath()
        clip.addEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.save()
        p.setClipPath(clip)
        for idx, ox in enumerate(MECH_GENEVA):
            p.setPen(QPen(MECH_STRIPE if idx % 2 == 0 else MECH_PLATE2, 5.0))
            p.drawLine(QLineF(cx + ox, cy - 200, cx + ox + 200, cy + 200))
        p.restore()
        p.setPen(QPen(MECH_STEEL_D, 1.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        # 弧形桥板 ×4（多边形近似弧，避免 arcTo 方向 bug；钢/玫瑰金交替）
        for bi, (a0, span) in enumerate([(18, 55), (108, 52), (198, 58), (288, 52)]):
            ro, ri = 143.0, 117.0
            pts = []
            for k in range(15):
                a = math.radians(a0 + span * k / 14.0)
                pts.append(QPointF(cx + ro * math.cos(a), cy + ro * math.sin(a)))
            for k in range(14, -1, -1):
                a = math.radians(a0 + span * k / 14.0)
                pts.append(QPointF(cx + ri * math.cos(a), cy + ri * math.sin(a)))
            g = QConicalGradient(cx, cy, a0)
            palette = ([(0.0, "#dbe2ea"), (0.5, "#59616c"), (1.0, "#cbd3dc")]
                       if bi % 2 == 0 else
                       [(0.0, "#e8c49a"), (0.5, "#7a5535"), (1.0, "#d6ab7e")])
            for pos, col in palette:
                g.setColorAt(pos, QColor(col))
            p.setPen(QPen(MECH_ROSE_D, 1.0))
            p.setBrush(QBrush(g))
            p.drawPolygon(QPolygonF(pts))
            # 桥板内外缘高光
            p.setPen(QPen(MECH_STEEL_L, 0.8))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolyline(QPolygonF(pts[:15]))
            p.setPen(QPen(MECH_STEEL_D, 0.5))
            p.drawPolyline(QPolygonF(pts[15:]))
            # 桥板两端螺丝沉孔（由 mm_screws 补上螺钉）
            for ka in (0.12, 0.88):
                a = math.radians(a0 + span * ka)
                rr = (ro + ri) / 2.0
                hx, hy = cx + rr * math.cos(a), cy + rr * math.sin(a)
                p.setPen(QPen(MECH_PLATE, 1.0))
                p.setBrush(QBrush(QColor(26, 28, 32)))
                p.drawEllipse(QRectF(hx - 4.2, hy - 4.2, 8.4, 8.4))

    def mm_chapter(self, p, cx, cy):
        """外圈：罗马数字时标（移至外圈，避开机械桥板）+ 分钟轨道。
        机械零件集中在 r≤143 的桥板区，故罗马数字放在 r=160 的黑色外圈带上。"""
        r_out, r_in = 181.0, 150.0
        p.setPen(QPen(MECH_ROSE, 1.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out))
        p.setPen(QPen(MECH_STEEL_D, 0.8))
        p.drawEllipse(QRectF(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in))
        # 分钟刻度（外移，紧贴外环，给内侧罗马数字让位）
        for i in range(60):
            a = math.radians(i * 6 - 90)
            major = (i % 5 == 0)
            r1 = 173 if major else 176
            pen = QPen(MECH_STEEL_L if major else MECH_STEEL_D, 1.5 if major else 0.6)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                              cx + 179 * math.cos(a), cy + 179 * math.sin(a)))
        # 罗马数字时标：放到外圈黑色带（r=160），彻底避开机械桥板与齿轮
        p.setFont(self.font_roman_out)
        for i, num in enumerate(ROMAN):
            a = math.radians(i * 30 - 90)
            tx, ty = cx + 160 * math.cos(a), cy + 160 * math.sin(a)
            p.drawText(QRectF(tx - 17, ty - 11, 34, 22), Qt.AlignmentFlag.AlignCenter, num)

    def mm_screws(self, p, cx, cy):
        """机芯固定螺丝（一字/十字槽 + 金属高光），与桥板沉孔对齐"""
        positions = [(24.6, 130), (66.4, 130), (114.2, 130), (153.8, 130),
                     (205.0, 130), (249.0, 130), (294.2, 130), (333.8, 130)]
        for idx, (ang, dist) in enumerate(positions):
            a = math.radians(ang)
            gx, gy = cx + dist * math.cos(a), cy + dist * math.sin(a)
            r = 4.6
            g = QRadialGradient(gx - 1.5, gy - 1.5, r * 1.4)
            g.setColorAt(0.0, MECH_STEEL_L)
            g.setColorAt(1.0, MECH_STEEL_D)
            p.setPen(QPen(MECH_PLATE, 0.8))
            p.setBrush(QBrush(g))
            p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
            slot = math.radians(ang + 40 + idx * 17)
            p.setPen(QPen(MECH_PLATE, 1.4))
            if idx % 3 == 0:
                for delta in (0.0, math.pi / 2):
                    sa = slot + delta
                    p.drawLine(QLineF(gx - r * 0.62 * math.cos(sa), gy - r * 0.62 * math.sin(sa),
                                      gx + r * 0.62 * math.cos(sa), gy + r * 0.62 * math.sin(sa)))
            else:
                p.drawLine(QLineF(gx - r * 0.7 * math.cos(slot), gy - r * 0.7 * math.sin(slot),
                                  gx + r * 0.7 * math.cos(slot), gy + r * 0.7 * math.sin(slot)))

    def mm_text(self, p, cx, cy):
        """机芯铭牌：繁体中文「陀飛輪」，置于盘心下方偏下位置。
        字体优先 Microsoft JhengHei（繁体字形正确），回退 YaHei / PMingLiU。
        底牌按文字实际宽度自适应；下移到 cy+132 后已避开两颗沉头螺丝
        （dist=130 角度 66.4°/114.2° → x=147/252, y=319，底牌横向仅 168~232 不与其相碰）。"""
        f = QFont()
        f.setFamilies(["Microsoft JhengHei", "Microsoft YaHei", "PMingLiU", "SimSun"])
        f.setPointSizeF(12.0)
        f.setBold(True)
        fm = QFontMetricsF(f)
        for text, ty in (("陀飛輪", cy + 132),):
            tw = fm.horizontalAdvance(text)
            pw = tw + 16.0               # 左右各 8 内边距
            ph = fm.height() + 5.0
            rect = QRectF(cx - pw / 2.0, ty - ph / 2.0, pw, ph)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(16, 18, 24, 220)))
            p.drawRoundedRect(rect, 5.0, 5.0)
            p.setPen(QPen(MECH_ROSE_D, 0.6))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect, 5.0, 5.0)
            p.setFont(f)
            p.setPen(QPen(MECH_TEXT))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def mm_jewel(self, p, gx, gy, r):
        """红宝石轴承：金色勒口 + 径向渐变宝石 + 高光"""
        p.setPen(QPen(MECH_ROSE_D, 0.9))
        p.setBrush(QBrush(MECH_ROSE))
        p.drawEllipse(QRectF(gx - r - 2.2, gy - r - 2.2, 2 * (r + 2.2), 2 * (r + 2.2)))
        g = QRadialGradient(gx - r * 0.3, gy - r * 0.3, r * 1.5)
        g.setColorAt(0.0, QColor(255, 120, 140))
        g.setColorAt(0.5, MECH_RUBY)
        g.setColorAt(1.0, QColor(105, 8, 26))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
        p.setBrush(QBrush(QColor(255, 225, 230, 170)))
        p.drawEllipse(QRectF(gx - r * 0.45, gy - r * 0.5, r * 0.6, r * 0.42))

    def mm_gear(self, p, gx, gy, r, teeth, ang, color):
        """标准模数齿轮：齿顶高=m、齿根深=1.25m、齿厚≈半齿距，保证与同模数齿轮真正咬合。
        r 为节圆半径（=m*teeth/2），齿顶圆 r+m、齿根圆 r-1.25m。"""
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        m = 2.0 * r / teeth
        r_add = r + m            # 齿顶圆
        r_ded = r - 1.25 * m      # 齿根圆
        step = 2.0 * math.pi / teeth
        pts = []
        for i in range(teeth):
            a = i * step
            # 梯形齿：齿根宽 ~0.5 齿距，齿顶宽 ~0.28 齿距，啮合点留齿槽
            for frac, rr in [(0.00, r_ded), (0.12, r_add),
                             (0.40, r_add), (0.52, r_ded),
                             (1.00, r_ded)]:
                aa = a + frac * step
                pts.append(QPointF(rr * math.cos(aa), rr * math.sin(aa)))
        g = QConicalGradient(0, 0, ang)
        g.setColorAt(0.0, color.lighter(150))
        g.setColorAt(0.28, color)
        g.setColorAt(0.55, color.darker(155))
        g.setColorAt(0.78, color)
        g.setColorAt(1.0, color.lighter(150))
        p.setPen(QPen(color.darker(190), 0.6))
        p.setBrush(QBrush(g))
        p.drawPolygon(QPolygonF(pts))
        # 车削同心刻线 + 齿圈铆钉（机加工质感）
        p.setPen(QPen(color.darker(140), 0.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-(r_ded - 1.6), -(r_ded - 1.6), 2 * (r_ded - 1.6), 2 * (r_ded - 1.6)))
        p.drawEllipse(QRectF(-(r - 3.2), -(r - 3.2), 2 * (r - 3.2), 2 * (r - 3.2)))
        for i in range(0, teeth, max(3, teeth // 12)):
            a = (i + 0.5) * step
            rr = r_ded - 3.2
            p.setPen(QPen(color.darker(175), 0.5))
            p.setBrush(QBrush(color.lighter(120)))
            p.drawEllipse(QRectF(rr * math.cos(a) - 0.9, rr * math.sin(a) - 0.9, 1.8, 1.8))
        # 轮辐镂空：更多辐条 + 高光边 + 轮辐铆点
        inner = r * 0.62
        p.setPen(QPen(color.darker(150), 0.9))
        p.setBrush(QBrush(MECH_PLATE))
        p.drawEllipse(QRectF(-inner, -inner, 2 * inner, 2 * inner))
        nspoke = 6 if r > 18 else 5
        spoke_w = max(1.8, r * 0.11)
        for k in range(nspoke):
            a = k * 2.0 * math.pi / nspoke
            ux, uy = math.cos(a), math.sin(a)
            p.setPen(QPen(color.lighter(125), spoke_w))
            p.drawLine(QLineF((r * 0.18) * ux, (r * 0.18) * uy,
                              (inner - 0.5) * ux, (inner - 0.5) * uy))
            p.setPen(QPen(color.lighter(180), 0.55))
            p.drawLine(QLineF((r * 0.22) * ux, (r * 0.22) * uy,
                              (inner - 1.6) * ux, (inner - 1.6) * uy))
            rr = inner * 0.74
            p.setPen(QPen(color.darker(155), 0.5))
            p.setBrush(QBrush(MECH_PLATE2))
            p.drawEllipse(QRectF(rr * ux - 1.5, rr * uy - 1.5, 3.0, 3.0))
        hub = r * 0.20
        g2 = QRadialGradient(-hub * 0.35, -hub * 0.35, hub * 1.5)
        g2.setColorAt(0.0, color.lighter(170))
        g2.setColorAt(1.0, color.darker(175))
        p.setPen(QPen(color.darker(185), 0.8))
        p.setBrush(QBrush(g2))
        p.drawEllipse(QRectF(-hub, -hub, 2 * hub, 2 * hub))
        p.setPen(QPen(color.lighter(165), 0.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-hub * 0.6, -hub * 0.6, 1.2 * hub, 1.2 * hub))
        p.restore()
        self.mm_jewel(p, gx, gy, min(4.2, r * 0.13))

    def mm_barrel(self, p, gx, gy, r, ang):
        """发条盒：齿圈 + 盒盖 + 内部可见发条（随盒慢转）"""
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        teeth = 52                       # 与 GEAR_TRAIN 一致
        m = 2.0 * r / teeth
        r_add, r_ded = r + m, r - 1.25 * m
        step = 2.0 * math.pi / teeth
        pts = []
        for i in range(teeth):
            a = i * step
            for frac, rr in [(0.00, r_ded), (0.12, r_add),
                             (0.40, r_add), (0.52, r_ded), (1.00, r_ded)]:
                aa = a + frac * step
                pts.append(QPointF(rr * math.cos(aa), rr * math.sin(aa)))
        g = QConicalGradient(0, 0, ang)
        for pos, col in [(0.0, "#dcae7e"), (0.3, "#8a5c34"), (0.6, "#e6bb8d"), (1.0, "#dcae7e")]:
            g.setColorAt(pos, QColor(col))
        p.setPen(QPen(MECH_ROSE_D, 0.6))
        p.setBrush(QBrush(g))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(QPen(MECH_ROSE_D, 1.0))
        p.setBrush(QBrush(QColor(36, 38, 44)))
        p.drawEllipse(QRectF(-r * 0.78, -r * 0.78, 1.56 * r, 1.56 * r))
        # 盒盖车削纹 + 八颗固定铆钉
        p.setPen(QPen(MECH_ROSE_D, 0.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-r * 0.72, -r * 0.72, 1.44 * r, 1.44 * r))
        p.drawEllipse(QRectF(-r * 0.64, -r * 0.64, 1.28 * r, 1.28 * r))
        for k in range(8):
            a = k * math.pi / 4
            rr = r * 0.70
            p.setPen(QPen(MECH_ROSE_D, 0.6))
            p.setBrush(QBrush(MECH_ROSE))
            p.drawEllipse(QRectF(rr * math.cos(a) - 1.4, rr * math.sin(a) - 1.4, 2.8, 2.8))
        p.restore()
        # 可见发条（阿基米德螺旋，铜色，随盒转）
        self_sp = r * 0.68
        n = 150
        spr = []
        for i in range(n):
            u = i / (n - 1.0)
            aa = u * math.pi * 2 * 3.6 + math.radians(ang)
            rr = 5.0 + u * (self_sp - 5.0)
            spr.append(QPointF(gx + rr * math.cos(aa), gy + rr * math.sin(aa)))
        p.setPen(QPen(MECH_ROSE_D, 2.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(QPolygonF(spr))
        p.setPen(QPen(MECH_ROSE.lighter(150), 1.0))
        p.drawPolyline(QPolygonF(spr))
        # 发条外端挂钩
        hx, hy = spr[-1].x(), spr[-1].y()
        p.setPen(QPen(MECH_ROSE_D, 1.0))
        p.setBrush(QBrush(MECH_ROSE))
        p.drawEllipse(QRectF(hx - 2.4, hy - 2.4, 4.8, 4.8))
        self.mm_jewel(p, gx, gy, 4.6)

    def mm_escape_spark(self, p, gx, gy, ang, s):
        """擒纵锁放火花：叉瓦刚锁定/释放擒纵轮齿（摆轮过零附近）时，瓦尖闪一点热光。"""
        # 摆轮过零（|s| 小）表示换向，即擒纵释放瞬间
        intensity = max(0.0, 1.0 - abs(s) / 0.28)
        if intensity <= 0.02:
            return
        ar = math.radians(ang)
        # 瓦尖在叉局部 +y 端偏 ±7.5
        m = GEAR_MODULE
        r_esc = _gear_radius(15)
        reach = 17.0 - (r_esc + m) + 1.0
        for sx in (-7.5, 7.5):
            wx = gx + reach * math.sin(ar) + sx * math.cos(ar)
            wy = gy - reach * math.cos(ar) + sx * math.sin(ar)
            a = int(150 * intensity)
            g = QRadialGradient(wx, wy, 7)
            g.setColorAt(0.0, QColor(255, 240, 200, a))
            g.setColorAt(0.4, QColor(255, 170, 80, a // 2))
            g.setColorAt(1.0, QColor(255, 120, 40, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(g))
            p.drawEllipse(QRectF(wx - 7, wy - 7, 14, 14))

    def mm_light_sweep(self, p, cx, cy, t):
        """金属反光扫带：一道柔和亮弧随时间绕盘心扫过，模拟蓝钢/钢件的高光流转。"""
        sweep = (t * 22.0) % 360.0
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(26):
            a = math.radians(sweep - i * 1.6)
            alpha = max(0, 16 - i)
            if alpha == 0:
                break
            p.setPen(QPen(QColor(220, 232, 248, alpha), 2.2))
            p.drawArc(QRectF(cx - 150, cy - 150, 300, 300),
                      int((-a * 180 / math.pi - 4) * 16), int(8 * 16))
        p.restore()

    # ---------- 外圈动态效果 ----------
    def mm_outer_fx(self, p, cx, cy, ctx, local):
        """外圈四项动态效果，均绘制在 r>160 的无零件区域（齿轮最外仅到 r≈116）：
          ① 秒点流光     —— 分钟轨道 r173~180，当前秒点亮 + 10 格渐隐光尾
          ② 昼夜弧       —— 玫瑰金环 r181.4~185，昼亮金 / 夜暗褐，日出日落处标记
          ③ 表壳光泽流转 —— 滚花 r187~196，一道光带绕壳流动
          ④ 年度进度环   —— r170.4 细轨 + 玫瑰金填充（春分起算太阳黄经）
        注意 drawArc 的笔宽以「框半径」为中线，故粗弧的框半径须取内外半径中值，
        否则弧带会整体外移。
        """
        t = local.timestamp()
        self.outer_second_glow(p, cx, cy, local)
        self.outer_day_night(p, cx, cy, ctx)
        self.outer_case_glint(p, cx, cy, t)
        self.outer_year_ring(p, cx, cy, ctx)

    def outer_second_glow(self, p, cx, cy, local):
        """① 秒点流光：当前秒刻度点亮为暖白，向后拖一串渐隐光尾，并带外圈光晕。
        光尾位置须对 60 秒取模，否则秒数 < 11 时 (sec-k) 为负、整条光尾会被跳过。"""
        sec = local.second + local.microsecond / 1e6
        # 光尾（先画远端，近端压在上面）
        for k in range(11, 0, -1):
            s = (sec - k) % 60.0
            a = math.radians(s * 6.0 - 90.0)
            alpha = int(170 * (1.0 - k / 12.0) ** 1.7)
            if alpha <= 4:
                continue
            pen = QPen(QColor(240, 186, 130, alpha), 1.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(cx + 173.5 * math.cos(a), cy + 173.5 * math.sin(a),
                              cx + 179.5 * math.cos(a), cy + 179.5 * math.sin(a)))
        a = math.radians(sec * 6.0 - 90.0)
        gx, gy = cx + 176.5 * math.cos(a), cy + 176.5 * math.sin(a)
        g = QRadialGradient(gx, gy, 9.0)
        g.setColorAt(0.0, QColor(255, 232, 190, 155))
        g.setColorAt(0.45, QColor(255, 205, 150, 62))
        g.setColorAt(1.0, QColor(255, 190, 130, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(gx - 9, gy - 9, 18, 18))
        # 当前秒刻度本体
        pen = QPen(QColor(255, 242, 212), 2.3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(cx + 171.8 * math.cos(a), cy + 171.8 * math.sin(a),
                          cx + 180.4 * math.cos(a), cy + 180.4 * math.sin(a)))

    def outer_day_night(self, p, cx, cy, ctx):
        """② 昼夜弧：玫瑰金外环按日出/日落分段——昼亮金、夜暗褐，交界放日/月标记。
        跨度直接用角度差（qt_ang 随小时递减，差值本身为负）。
        若套 %360 会把 -156° 变成 +204°，昼长 10.4h 被画成 13.6h 且夜段跨度为 0 而不绘制。
        """
        r_out, r_in = 185.0, 181.4
        r_mid = (r_out + r_in) / 2.0
        wdt = r_out - r_in
        rect = QRectF(cx - r_mid, cy - r_mid, 2 * r_mid, 2 * r_mid)
        sunrise, sunset = ctx.get("sunrise", 6.0), ctx.get("sunset", 18.0)

        def qt_ang(hour):
            """12 时在上、24h 一周的 Qt 角度（逆时针为正）。"""
            return 90.0 - ((hour - 12.0) / 24.0) * 360.0

        # 夜：整圈暗褐打底
        pen = QPen(QColor(74, 64, 62), wdt)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)
        # 昼：日出 → 日落
        a0, a1 = qt_ang(sunrise), qt_ang(sunset)
        pen = QPen(QColor(246, 208, 156), wdt)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.drawArc(rect, int(a0 * 16), int((a1 - a0) * 16))
        # 交界标记（qt_ang 已是 Qt 角，数学坐标须 y=-sin，不能再减 90）
        for hour, is_sun in ((sunrise, True), (sunset, False)):
            aa = math.radians(qt_ang(hour))
            mx = cx + 183.2 * math.cos(aa)
            my = cy - 183.2 * math.sin(aa)
            if is_sun:
                g = QRadialGradient(mx, my, 5.0)
                g.setColorAt(0.0, QColor(255, 255, 240))
                g.setColorAt(0.5, QColor(255, 216, 132))
                g.setColorAt(1.0, QColor(255, 200, 110, 20))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(g))
                p.drawEllipse(QRectF(mx - 5.0, my - 5.0, 10.0, 10.0))
            else:
                p.setPen(QPen(QColor(240, 228, 214), 1.0))
                p.setBrush(QBrush(QColor(232, 222, 212)))
                p.drawEllipse(QRectF(mx - 3.6, my - 3.6, 7.2, 7.2))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(QColor(74, 64, 62)))
                p.drawEllipse(QRectF(mx - 1.1, my - 4.5, 6.8, 6.8))

    def outer_case_glint(self, p, cx, cy, t):
        """③ 表壳光泽流转：一道光带绕壳转动，依次提亮经过的滚花刻线。
        滚花本身是亮钢色（L≈175），单靠提亮对比不足，故先压暗整圈再叠加高光，
        形成「暗—亮—暗」的流动明暗带。气氛光须裁到表壳圆内，否则会溢出盘外形成白团。"""
        sweep = (t * 15.0) % 360.0
        # 1) 整圈压暗（把滚花压成底色，留出明暗落差）
        #    用粗笔描一圈代替「两椭圆做 OddEven 填充的路径」——等价但快得多。
        r_mid_case = (196.5 + 186.2) / 2.0
        pen = QPen(QColor(8, 10, 14, 110), 196.5 - 186.2)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_mid_case, cy - r_mid_case,
                             2 * r_mid_case, 2 * r_mid_case))
        # 2) 光带提亮经过的刻线：只遍历光带覆盖的 ±70° 区间（约 70 条），
        #    不再扫描全部 180 条并逐条剔除，省去大量空转分支。
        start = int((sweep - 70.0) / 2.0)
        for i in range(start, start + 71):
            ang = (i * 2.0) % 360.0
            d = abs((ang - sweep + 180.0) % 360.0 - 180.0)
            if d > 70.0:
                continue
            k = math.cos(math.radians(d / 70.0 * 90.0)) ** 1.5
            alpha = int(255 * k)
            if alpha <= 6:
                continue
            a = math.radians(ang)
            pen = QPen(QColor(255, 252, 246, alpha), 2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(cx + 186.5 * math.cos(a), cy + 186.5 * math.sin(a),
                              cx + 196.0 * math.cos(a), cy + 196.0 * math.sin(a)))
        # 3) 壳面气氛光（裁到表壳圆内）
        p.save()
        clip2 = QPainterPath()
        clip2.addEllipse(QRectF(cx - 196.0, cy - 196.0, 392.0, 392.0))
        p.setClipPath(clip2)
        aa = math.radians(sweep)
        gx, gy = cx + 191.0 * math.cos(aa), cy + 191.0 * math.sin(aa)
        g = QRadialGradient(gx, gy, 30.0)
        g.setColorAt(0.0, QColor(255, 250, 240, 95))
        g.setColorAt(1.0, QColor(255, 240, 220, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(gx - 30, gy - 30, 60, 60))
        p.restore()

    def outer_year_ring(self, p, cx, cy, ctx):
        """④ 年度进度环：r=170.4 细轨 + 玫瑰金填充，自春分顺时针累计太阳黄经。
        该半径落在实测干净带内（整圈标准差≈8），不与罗马数字墨迹、分钟刻度相碰。"""
        r = 170.4
        rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
        p.setPen(QPen(QColor(58, 66, 80, 210), 2.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)
        deg = ctx.get("sun_lon", 0.0) % 360.0
        p.setPen(QPen(MECH_ROSE, 2.0))
        p.drawArc(rect, 90 * 16, int(-deg * 16))
        # 二分二至刻度
        for d in (0.0, 90.0, 180.0, 270.0):
            a = math.radians(90.0 - d)
            p.setPen(QPen(QColor(126, 134, 148, 190), 1.0))
            p.drawLine(QLineF(cx + (r - 2.2) * math.cos(a), cy - (r - 2.2) * math.sin(a),
                              cx + (r + 2.2) * math.cos(a), cy - (r + 2.2) * math.sin(a)))
        # 春分起点 + 当前进度点
        for d, col, rr in ((0.0, QColor(146, 106, 68), 2.0),
                           (deg, QColor(252, 214, 170), 2.8)):
            a = math.radians(90.0 - d)
            mx, my = cx + r * math.cos(a), cy - r * math.sin(a)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(col))
            p.drawEllipse(QRectF(mx - rr, my - rr, 2 * rr, 2 * rr))

    def _build_tourbillon_pm(self):
        """预渲染陀飞轮框架（外圈+辐条+桥板+螺钉+配重）到 2x 透明贴图，绘制时只旋转。"""
        dpr = 2
        R = TOURB_CAGE_R
        half = R + 5.0
        pm = QPixmap(int(2 * half * dpr), int(2 * half * dpr))
        pm.fill(QColor(0, 0, 0, 0))
        q = QPainter(pm)
        q.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        q.scale(dpr, dpr)
        q.translate(half, half)

        # 抛光钢外圈（锥形渐变）
        g = QConicalGradient(0, 0, 20)
        for pos, col in [(0.0, "#e6edf5"), (0.18, "#67717e"), (0.42, "#cfd8e2"),
                         (0.68, "#4d5560"), (0.9, "#b8c2cf"), (1.0, "#e6edf5")]:
            g.setColorAt(pos, QColor(col))
        q.setPen(QPen(QBrush(g), 4.2))
        q.setBrush(Qt.BrushStyle.NoBrush)
        q.drawEllipse(QRectF(-R + 2, -R + 2, 2 * (R - 2), 2 * (R - 2)))
        q.setPen(QPen(MECH_STEEL_D, 0.9))
        q.drawEllipse(QRectF(-R + 5.2, -R + 5.2, 2 * (R - 5.2), 2 * (R - 5.2)))
        q.setPen(QPen(MECH_STEEL_L, 0.7))
        q.drawEllipse(QRectF(-R - 0.6, -R - 0.6, 2 * (R + 0.6), 2 * (R + 0.6)))
        # 外圈刻度（每 15°，整点加长）
        for k in range(24):
            a = k * math.pi / 12
            r0 = R - 4.5
            r1 = R - (1.5 if k % 2 == 0 else 3.0)
            q.setPen(QPen(MECH_STEEL_L if k % 2 == 0 else MECH_STEEL_D, 0.7))
            q.drawLine(QLineF(r0 * math.cos(a), r0 * math.sin(a),
                              r1 * math.cos(a), r1 * math.sin(a)))
        # 三根锥形辐条 + 固定螺钉
        for k in range(3):
            a = math.radians(k * 120 - 90)
            ux, uy = math.cos(a), math.sin(a)
            vx, vy = -uy, ux
            poly = [QPointF(9 * ux + 2.4 * vx, 9 * uy + 2.4 * vy),
                    QPointF((R - 4) * ux + 1.4 * vx, (R - 4) * uy + 1.4 * vy),
                    QPointF((R - 4) * ux - 1.4 * vx, (R - 4) * uy - 1.4 * vy),
                    QPointF(9 * ux - 2.4 * vx, 9 * uy - 2.4 * vy)]
            q.setPen(QPen(MECH_STEEL_D, 0.8))
            q.setBrush(QBrush(QColor(150, 162, 178)))
            q.drawPolygon(QPolygonF(poly))
            q.setPen(QPen(MECH_STEEL_L, 0.5))
            q.drawLine(QLineF(10 * ux + vx, 10 * uy + vy,
                              (R - 6) * ux + vx, (R - 6) * uy + vy))
            sx, sy = (R - 2.2) * ux, (R - 2.2) * uy
            q.setPen(QPen(MECH_STEEL_D, 0.7))
            q.setBrush(QBrush(MECH_ROSE))
            q.drawEllipse(QRectF(sx - 3, sy - 3, 6, 6))
            q.setPen(QPen(MECH_ROSE_D, 0.9))
            q.drawLine(QLineF(sx - 2 * ux, sy - 2 * uy, sx + 2 * ux, sy + 2 * uy))
        # 弧形钢桥（跨越框架上方）
        a0, a1 = math.radians(20), math.radians(78)
        seg = 18
        ro, ri = R - 1.0, R - 10.0
        outer = [QPointF(ro * math.cos(a0 + (a1 - a0) * k / seg),
                         ro * math.sin(a0 + (a1 - a0) * k / seg)) for k in range(seg + 1)]
        inner = [QPointF(ri * math.cos(a0 + (a1 - a0) * k / seg),
                         ri * math.sin(a0 + (a1 - a0) * k / seg)) for k in range(seg, -1, -1)]
        gb = QLinearGradient(-R, -R, R, R)
        gb.setColorAt(0.0, QColor("#d8e0ea"))
        gb.setColorAt(0.5, QColor("#6d7683"))
        gb.setColorAt(1.0, QColor("#c3ccd8"))
        q.setPen(QPen(MECH_STEEL_D, 0.9))
        q.setBrush(QBrush(gb))
        q.drawPolygon(QPolygonF(outer + inner))
        q.setPen(QPen(MECH_STEEL_L, 0.6))
        q.setBrush(Qt.BrushStyle.NoBrush)
        q.drawPolyline(QPolygonF(outer))
        for a in (a0, a1):
            sx, sy = (R - 5.5) * math.cos(a), (R - 5.5) * math.sin(a)
            q.setPen(QPen(MECH_STEEL_D, 0.6))
            q.setBrush(QBrush(MECH_STEEL_L))
            q.drawEllipse(QRectF(sx - 2.4, sy - 2.4, 4.8, 4.8))
        # 中心毂（环形，露出中心擒纵轮宝石）
        q.setPen(QPen(QBrush(g), 2.6))
        q.setBrush(Qt.BrushStyle.NoBrush)
        q.drawEllipse(QRectF(-10, -10, 20, 20))
        q.setPen(QPen(MECH_ROSE, 0.8))
        q.drawEllipse(QRectF(-6.5, -6.5, 13, 13))
        # 玫瑰金配重块
        aw = math.radians(250)
        wx, wy = (R - 14) * math.cos(aw), (R - 14) * math.sin(aw)
        q.setPen(QPen(MECH_ROSE_D, 0.8))
        q.setBrush(QBrush(MECH_ROSE))
        q.drawEllipse(QRectF(wx - 5, wy - 5, 10, 10))
        q.end()
        return pm, half

    def mm_tourbillon(self, p, gx, gy, ang):
        """陀飞轮框架：预渲染贴图层随框架旋转；中心轴宝石留给擒纵轮。"""
        if self.tourb_pm is None:
            self.tourb_pm, self.tourb_half = self._build_tourbillon_pm()
        half = self.tourb_half
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        p.drawPixmap(QRectF(-half, -half, 2 * half, 2 * half), self.tourb_pm,
                     QRectF(0, 0, self.tourb_pm.width(), self.tourb_pm.height()))
        p.restore()

    def mm_moon_subdial(self, p, gx, gy, elong):
        """月相副盘：真实日月黄经差驱动的月相 + 星空 + 金属表圈。"""
        r = SUB_R
        p.setPen(QPen(MECH_ROSE_D, 1.4))
        p.setBrush(QBrush(QColor(12, 16, 24)))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
        p.setPen(QPen(MECH_STEEL_L, 0.7))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(gx - r + 2.4, gy - r + 2.4, 2 * (r - 2.4), 2 * (r - 2.4)))
        # 点缀星
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(210, 220, 240)))
        for dx, dy, s in [(-10, -7, 0.9), (9, -9, 1.0), (11, 7, 0.8), (-9, 9, 0.7)]:
            p.drawEllipse(QRectF(gx + dx - s, gy + dy - s, 2 * s, 2 * s))
        # 月相明暗界线
        mr = r - 6.0
        waxing = elong < 180.0
        c = math.cos(math.radians(elong))
        pts = []
        steps = 36
        for i in range(steps + 1):
            y = -mr + 2 * mr * i / steps
            w = math.sqrt(max(0.0, mr * mr - y * y))
            pts.append(QPointF(gx + (c * w if waxing else -w), gy + y))
        for i in range(steps, -1, -1):
            y = -mr + 2 * mr * i / steps
            w = math.sqrt(max(0.0, mr * mr - y * y))
            pts.append(QPointF(gx + (w if waxing else -c * w), gy + y))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(ASTRO_MOON))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(QPen(MECH_ROSE_D, 0.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(gx - mr, gy - mr, 2 * mr, 2 * mr))

    def mm_power_subdial(self, p, gx, gy, t):
        """动力储存副盘：指针式，在 E(空)↔F(满) 之间缓慢扫动。"""
        r = SUB_R
        p.setPen(QPen(MECH_ROSE_D, 1.4))
        p.setBrush(QBrush(QColor(12, 16, 24)))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
        p.setPen(QPen(MECH_STEEL_L, 0.7))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(gx - r + 2.4, gy - r + 2.4, 2 * (r - 2.4), 2 * (r - 2.4)))
        # 弧形刻度
        a0, a1 = 150.0, 390.0
        for k in range(13):
            a = math.radians(a0 + (a1 - a0) * k / 12)
            ro = r - 4.0
            ri = ro - (3.5 if k % 3 == 0 else 2.0)
            p.setPen(QPen(MECH_STEEL_L if k % 3 == 0 else MECH_STEEL_D,
                          0.9 if k % 3 == 0 else 0.6))
            p.drawLine(QLineF(gx + ri * math.cos(a), gy + ri * math.sin(a),
                              gx + ro * math.cos(a), gy + ro * math.sin(a)))
        # 低储备红区
        p.setPen(QPen(QColor(190, 60, 50), 2.0))
        p.drawArc(QRectF(gx - r + 4, gy - r + 4, 2 * (r - 4), 2 * (r - 4)),
                  int(a0 * 16), int(30 * 16))
        # 指针（平滑往复，无跳变）
        frac = 0.5 + 0.5 * math.sin(2.0 * math.pi * t / 100.0)
        na = math.radians(a0 + (a1 - a0) * frac)
        p.setPen(QPen(MECH_ROSE, 1.8))
        p.drawLine(QLineF(gx, gy, gx + (r - 6) * math.cos(na),
                          gy + (r - 6) * math.sin(na)))
        self.mm_jewel(p, gx, gy, 2.8)

    def mm_date_subdial(self, p, gx, gy, local):
        """星期日期副盘（左上）：月名 / 日期大字 / 星期，全部由本地真实日期驱动。"""
        r = SUB_R
        p.setPen(QPen(MECH_ROSE_D, 1.4))
        p.setBrush(QBrush(QColor(12, 16, 24)))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
        p.setPen(QPen(MECH_STEEL_L, 0.7))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(gx - r + 2.4, gy - r + 2.4, 2 * (r - 2.4), 2 * (r - 2.4)))
        # 月名（英文三字母缩写，小字置顶）
        f_mon = QFont("Georgia", 5)
        f_mon.setBold(True)
        p.setFont(f_mon)
        p.setPen(QPen(MECH_STEEL_L))
        p.drawText(QRectF(gx - 16, gy - 16, 32, 8), Qt.AlignmentFlag.AlignCenter,
                   local.strftime("%b").upper())
        # 日期大字
        f_day = QFont("Georgia", 12)
        f_day.setBold(True)
        p.setFont(f_day)
        p.setPen(QPen(MECH_STEEL_L))
        p.drawText(QRectF(gx - 16, gy - 10, 32, 14), Qt.AlignmentFlag.AlignCenter,
                   "%d" % local.day)
        # 星期（中文，玫瑰金）
        p.setFont(self.font_sub_cn)
        p.setPen(QPen(MECH_ROSE))
        p.drawText(QRectF(gx - 16, gy + 3, 32, 9), Qt.AlignmentFlag.AlignCenter,
                   WEEK_CN[local.weekday()])

    def mm_term_subdial(self, p, gx, gy, term, prog):
        """二十四节气副盘（右下）：24 等分刻度环 + 当前节气进度弧与指针 + 中心节气名。"""
        r = SUB_R
        p.setPen(QPen(MECH_ROSE_D, 1.4))
        p.setBrush(QBrush(QColor(12, 16, 24)))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
        p.setPen(QPen(MECH_STEEL_L, 0.7))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(gx - r + 2.4, gy - r + 2.4, 2 * (r - 2.4), 2 * (r - 2.4)))
        try:
            idx = SOLAR_TERMS.index(term)
        except ValueError:
            idx = 0
        # 24 格刻度：每 15° 一节；二分二至（每 6 节）加长加亮
        span = prog * 15.0
        for k in range(24):
            a = math.radians(k * 15.0 - 90.0)
            major = (k % 6 == 0)
            ro = r - 3.2
            ri = ro - (3.6 if major else 1.9)
            p.setPen(QPen(MECH_STEEL_L if major else MECH_STEEL_D,
                          0.9 if major else 0.5))
            p.drawLine(QLineF(gx + ri * math.cos(a), gy + ri * math.sin(a),
                              gx + ro * math.cos(a), gy + ro * math.sin(a)))
        # 年进度环：整圈暗色轨道 + 玫瑰金填充弧（从春分 0° 累计到当前太阳黄经）
        # 节气按太阳黄经每 15° 一节，故 arc 长度即"这一年已走过的节气进度"，语义直观
        arc_r = r - 5.2
        arc_rect = QRectF(gx - arc_r, gy - arc_r, 2 * arc_r, 2 * arc_r)
        p.setPen(QPen(QColor(74, 82, 94), 0.9))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(arc_rect, 0, 360 * 16)
        year_deg = idx * 15.0 + span
        if year_deg > 0.5:
            p.setPen(QPen(MECH_ROSE, 1.5))
            p.drawArc(arc_rect, 90 * 16, int(-year_deg * 16))
            # 弧线末端亮点：标示"当前走到这里"，避免与白刻度叠加成十字
            ea = math.radians(90.0 - year_deg)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(226, 176, 120)))
            p.drawEllipse(QRectF(gx + arc_r * math.cos(ea) - 1.5,
                                 gy - arc_r * math.sin(ea) - 1.5, 3.0, 3.0))
        # 当前节气名（真实中文节气），居中放在空出的内核区
        f_term = QFont("Microsoft YaHei", 6)
        f_term.setBold(True)
        p.setFont(f_term)
        p.setPen(QPen(MECH_STEEL_L))
        p.drawText(QRectF(gx - 15, gy - 5.5, 30, 11), Qt.AlignmentFlag.AlignCenter, term)

    def _build_rotor_pm(self):
        """预渲染自动陀旋转体（齿圈+配重+滚花+刻字）到 2x 透明贴图，绘制时只旋转。"""
        dpr = 2
        m = GEAR_MODULE
        z = ROTOR_TEETH
        r_pitch = m * z / 2.0
        r_tip = r_pitch - m
        r_root = r_pitch + 1.25 * m
        r_out = r_root + 5.0
        half = r_out + 4.0
        pm = QPixmap(int(2 * half * dpr), int(2 * half * dpr))
        pm.fill(QColor(0, 0, 0, 0))
        q = QPainter(pm)
        q.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        q.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        q.scale(dpr, dpr)
        q.translate(half, half)
        step = 2.0 * math.pi / z

        # 内齿圈（齿朝内）
        ring = []
        for i in range(z):
            a = i * step
            for frac, rr in [(0.00, r_root), (0.14, r_tip),
                             (0.40, r_tip), (0.54, r_root), (1.00, r_root)]:
                aa = a + frac * step
                ring.append(QPointF(rr * math.cos(aa), rr * math.sin(aa)))
        outer = [QPointF(r_out * math.cos(i * step), r_out * math.sin(i * step))
                 for i in range(z)]
        path = QPainterPath()
        path.addPolygon(QPolygonF(outer))
        hole = QPainterPath()
        hole.addPolygon(QPolygonF(ring))
        path = path.subtracted(hole)
        g = QConicalGradient(0, 0, 40)
        for pos, col in [(0.0, "#f0d3a8"), (0.2, "#8a5b35"), (0.45, "#e8c393"),
                         (0.7, "#6e4325"), (0.9, "#d8ad7c"), (1.0, "#f0d3a8")]:
            g.setColorAt(pos, QColor(col))
        q.setPen(QPen(MECH_ROSE_D, 0.8))
        q.setBrush(QBrush(g))
        q.drawPath(path)
        q.setPen(QPen(QColor(255, 226, 180, 150), 0.5))
        q.setBrush(Qt.BrushStyle.NoBrush)
        q.drawPolygon(QPolygonF(ring))
        # 外缘滚花
        q.setPen(QPen(MECH_ROSE_D, 0.7))
        for i in range(0, z, 2):
            a = i * step
            q.drawLine(QLineF(r_out * math.cos(a), r_out * math.sin(a),
                              (r_out + 2.2) * math.cos(a), (r_out + 2.2) * math.sin(a)))

        # 半圆配重（扇形环，镂空）
        # ro 需小于 auto 轮中心距盘心(≈105)，否则盖住 auto 轮与内齿圈的咬合区
        a0, a1 = math.radians(-88), math.radians(88)
        ri, ro = r_pitch - 46.0, r_pitch - 19.0
        seg = 40
        arc_out = [QPointF(ro * math.cos(a0 + (a1 - a0) * k / seg),
                           ro * math.sin(a0 + (a1 - a0) * k / seg)) for k in range(seg + 1)]
        arc_in = [QPointF(ri * math.cos(a0 + (a1 - a0) * k / seg),
                          ri * math.sin(a0 + (a1 - a0) * k / seg)) for k in range(seg, -1, -1)]
        gw = QConicalGradient(0, 0, 20)
        for pos, col in [(0.0, "#3a3f48"), (0.35, "#8e97a3"), (0.6, "#4a515c"),
                         (1.0, "#2b3038")]:
            gw.setColorAt(pos, QColor(col))
        q.setPen(QPen(MECH_STEEL_D, 1.0))
        q.setBrush(QBrush(gw))
        q.drawPolygon(QPolygonF(arc_out + arc_in))
        q.setPen(QPen(MECH_STEEL_L, 0.7))
        q.setBrush(Qt.BrushStyle.NoBrush)
        q.drawPolyline(QPolygonF(arc_out))
        for k in (-1, 0, 1):
            a = math.radians(k * 42)
            rr = (ri + ro) / 2.0
            wx, wy = rr * math.cos(a), rr * math.sin(a)
            q.setPen(QPen(MECH_STEEL_D, 0.7))
            q.setBrush(QBrush(QColor(10, 12, 16, 90)))
            q.drawEllipse(QRectF(wx - 7, wy - 5.5, 14, 11))
            q.setPen(QPen(MECH_STEEL_L, 0.4))
            q.setBrush(Qt.BrushStyle.NoBrush)
            q.drawEllipse(QRectF(wx - 7, wy - 5.5, 14, 11))
        q.end()
        return pm, half

    def mm_rotor(self, p, cx, cy, ang):
        """自动陀：预渲染旋转体贴图层 + 固定中心轴宝石。内齿圈与 auto 轮严格内啮合。"""
        if self.rotor_pm is None:
            self.rotor_pm, self.rotor_half = self._build_rotor_pm()
        half = self.rotor_half
        p.save()
        p.translate(cx, cy)
        p.rotate(ang)
        p.drawPixmap(QRectF(-half, -half, 2 * half, 2 * half), self.rotor_pm,
                     QRectF(0, 0, self.rotor_pm.width(), self.rotor_pm.height()))
        p.restore()
        # 中心轴 + 轴承宝石（不随陀转）
        p.setPen(QPen(MECH_ROSE_D, 1.0))
        p.setBrush(QBrush(MECH_ROSE))
        p.drawEllipse(QRectF(cx - 9, cy - 9, 18, 18))
        self.mm_jewel(p, cx, cy, 4.4)

    def mm_ratchet(self, p, gx, gy, r, teeth, ang):
        """棘轮：外圈为与条盒/皇冠轮咬合的标准模数齿轮，内部为单向棘齿 + 棘爪。"""
        m = 2.0 * r / teeth
        r_add, r_ded = r + m, r - 1.25 * m
        step = 2.0 * math.pi / teeth
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        # 外齿圈（与条盒轮、皇冠轮严格咬合的梯形齿）
        pts = []
        for i in range(teeth):
            a = i * step
            for frac, rr in [(0.0, r_ded), (0.12, r_add),
                             (0.40, r_add), (0.52, r_ded), (1.0, r_ded)]:
                aa = a + frac * step
                pts.append(QPointF(rr * math.cos(aa), rr * math.sin(aa)))
        g = QConicalGradient(0, 0, ang)
        for pos, col in [(0.0, "#efc99a"), (0.3, "#9c6c3e"),
                         (0.65, "#dfb17f"), (1.0, "#efc99a")]:
            g.setColorAt(pos, QColor(col))
        p.setPen(QPen(MECH_ROSE_D, 0.6))
        p.setBrush(QBrush(g))
        p.drawPolygon(QPolygonF(pts))
        # 内部单向棘齿（陡边 + 斜边，不对称）
        ri = r * 0.74
        n = 13
        cs = 2.0 * math.pi / n
        saw = []
        for i in range(n):
            a = i * cs
            saw.append(QPointF(ri * math.cos(a), ri * math.sin(a)))
            saw.append(QPointF((ri - 4.2) * math.cos(a + 0.72 * cs),
                               (ri - 4.2) * math.sin(a + 0.72 * cs)))
        p.setPen(QPen(MECH_ROSE_D, 0.7))
        p.setBrush(QBrush(MECH_PLATE))
        p.drawPolygon(QPolygonF(saw))
        p.setPen(QPen(MECH_ROSE_D, 0.8))
        p.setBrush(QBrush(MECH_ROSE_D))
        p.drawEllipse(QRectF(-r * 0.30, -r * 0.30, r * 0.60, r * 0.60))
        p.restore()
        # 止逆棘爪（固定轴，尖端搭在棘齿外沿）
        ca = math.radians(-58.0)
        px, py = gx + (r + 8.0) * math.cos(ca), gy + (r + 8.0) * math.sin(ca)
        tx, ty = gx + (r - 2.0) * math.cos(ca + 0.18), gy + (r - 2.0) * math.sin(ca + 0.18)
        p.setPen(QPen(MECH_STEEL_D, 2.4))
        p.drawLine(QLineF(px, py, tx, ty))
        p.setPen(QPen(MECH_STEEL_D, 0.9))
        p.setBrush(QBrush(MECH_STEEL_L))
        p.drawEllipse(QRectF(px - 3.2, py - 3.2, 6.4, 6.4))
        self.mm_jewel(p, gx, gy, 3.6)

    def mm_escape_wheel(self, p, gx, gy, r, ang):
        """擒纵轮：15 枚尖齿，每半摆动周期步进一格"""
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        teeth = 15
        m = 2.0 * r / teeth
        r_add, r_ded = r + m, r - 1.25 * m
        step = 2.0 * math.pi / teeth
        pts = []
        for i in range(teeth):
            a = i * step
            # 擒纵轮尖齿：也是同模数，确保与四轮啮合点齿距一致
            for frac, rr in [(0.00, r_ded), (0.18, r_add),
                             (0.44, r_add), (0.56, r_ded), (1.00, r_ded)]:
                aa = a + frac * step
                pts.append(QPointF(rr * math.cos(aa), rr * math.sin(aa)))
        g = QConicalGradient(0, 0, ang)
        g.setColorAt(0.0, MECH_STEEL_L)
        g.setColorAt(0.5, MECH_STEEL_D)
        g.setColorAt(1.0, MECH_STEEL_L)
        p.setPen(QPen(MECH_STEEL_D, 0.6))
        p.setBrush(QBrush(g))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(QPen(MECH_STEEL_D, 0.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-r * 0.62, -r * 0.62, 1.24 * r, 1.24 * r))
        for k in range(6):
            a = k * math.pi / 3
            p.setPen(QPen(MECH_STEEL, max(1.6, r * 0.09)))
            p.drawLine(QLineF((r * 0.16) * math.cos(a), (r * 0.16) * math.sin(a),
                              (r * 0.60) * math.cos(a), (r * 0.60) * math.sin(a)))
        hub = r * 0.20
        p.setPen(QPen(MECH_STEEL_D, 0.7))
        p.setBrush(QBrush(MECH_STEEL))
        p.drawEllipse(QRectF(-hub, -hub, 2 * hub, 2 * hub))
        p.restore()
        self.mm_jewel(p, gx, gy, 3.0)

    def mm_pallet_fork(self, p, gx, gy, ang, slot_len=22.0, frame_ang=0.0):
        """擒纵叉：局部 -y 端为叉口(咬住摆轮圆盘钉)，+y 端两红宝石瓦搭在擒纵轮齿上。
        由圆盘钉驱动绕轴摆动，实现 摆轮→叉→擒纵轮 的物理咬合链。"""
        m = GEAR_MODULE
        r_esc = _gear_radius(15)              # 擒纵轮节圆半径
        pallet_reach = 17.0 - (r_esc + m) + 1.0   # 瓦尖到叉轴距离：刚好搭上擒纵轮齿圈
        p.save()
        p.translate(gx, gy)
        p.rotate(ang)
        # 叉身：从叉口(-slot_len)到瓦臂(+pallet_reach)的 Y 形杠杆
        body = [QPointF(-2.6, -slot_len), QPointF(2.6, -slot_len),
                QPointF(3.0, -slot_len + 7), QPointF(2.2, pallet_reach * 0.3),
                QPointF(9.0, pallet_reach), QPointF(6.0, pallet_reach + 2),
                QPointF(0, pallet_reach * 0.55),
                QPointF(-6.0, pallet_reach + 2), QPointF(-9.0, pallet_reach),
                QPointF(-2.2, pallet_reach * 0.3), QPointF(-3.0, -slot_len + 7)]
        p.setPen(QPen(MECH_STEEL_D, 0.8))
        p.setBrush(QBrush(MECH_STEEL))
        p.drawPolygon(QPolygonF(body))
        # 叉口 U 形槽（包住圆盘钉）：末端的两颗挡角
        p.setPen(QPen(MECH_STEEL_L, 1.4))
        p.drawLine(QLineF(-2.6, -slot_len, -5.0, -slot_len - 3.5))
        p.drawLine(QLineF(2.6, -slot_len, 5.0, -slot_len - 3.5))
        # 两颗红宝石瓦（金色镶座 + 宝石，随叉摆动一锁一放）
        for sx in (-7.5, 7.5):
            p.setPen(QPen(MECH_ROSE_D, 0.6))
            p.setBrush(QBrush(MECH_ROSE))
            p.drawEllipse(QRectF(sx - 3.3, pallet_reach - 1.4, 6.6, 7.4))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(MECH_RUBY))
            p.drawEllipse(QRectF(sx - 2.6, pallet_reach - 1.0, 5.2, 6.5))
            p.setBrush(QBrush(QColor(255, 200, 210, 200)))
            p.drawEllipse(QRectF(sx - 1.8, pallet_reach - 0.6, 2.0, 1.6))
        # 叉身调节螺钉
        p.setPen(QPen(MECH_STEEL_D, 0.6))
        p.setBrush(QBrush(MECH_STEEL_L))
        p.drawEllipse(QRectF(-1.6, -slot_len + 9, 3.2, 3.2))
        p.restore()
        # 限位钉（固定在框架上，随框架一起公转）
        fa = math.radians(frame_ang)
        for off in (-1, 1):
            lx, ly = off * 10.5, 5.0
            ax = gx + lx * math.cos(fa) - ly * math.sin(fa)
            ay = gy + lx * math.sin(fa) + ly * math.cos(fa)
            p.setPen(QPen(MECH_STEEL_D, 0.8))
            p.setBrush(QBrush(MECH_STEEL))
            p.drawEllipse(QRectF(ax - 2.2, ay - 2.2, 4.4, 4.4))
        self.mm_jewel(p, gx, gy, 3.2)

    def mm_balance(self, p, gx, gy, r, bal_ang, s, pin=None, pin_base=0.0,
                   pin_r=11.0, frame_ang=0.0):
        """摆轮（随摆动+框架公转旋转）+ 游丝（真实呼吸）+ 圆盘钉（驱动擒纵叉）。
        pin 为圆盘钉当前世界坐标；pin_base 为其 0 相位时在摆轮上的固定角。
        pin_r 圆盘钉回转半径；frame_ang 陀飞轮框架公转角（游丝外桩随之公转）。"""
        # 摆轮本体
        p.save()
        p.translate(gx, gy)
        p.rotate(bal_ang)
        g = QConicalGradient(0, 0, bal_ang)
        g.setColorAt(0.0, MECH_ROSE_D)
        g.setColorAt(0.35, MECH_ROSE.lighter(140))
        g.setColorAt(0.65, MECH_ROSE)
        g.setColorAt(1.0, MECH_ROSE_D)
        p.setPen(QPen(MECH_ROSE_D, 1.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-r + 5, -r + 5, 2 * (r - 5), 2 * (r - 5)))
        p.setPen(QPen(g, 4.0))
        p.drawEllipse(QRectF(-r + 7, -r + 7, 2 * (r - 7), 2 * (r - 7)))
        p.setPen(QPen(MECH_STEEL_L, 0.8))
        p.drawEllipse(QRectF(-r + 3, -r + 3, 2 * (r - 3), 2 * (r - 3)))
        # 摆轮辐条（4 根）+ 8 颗配重螺丝（带一字槽）
        for k in range(4):
            a = math.radians(k * 90)
            p.setPen(QPen(MECH_STEEL, 3.0))
            p.drawLine(QLineF(0, 0, (r - 7) * math.cos(a), (r - 7) * math.sin(a)))
        for k in range(8):
            a = math.radians(k * 45 + 22.5)
            bx, by = (r - 5.5) * math.cos(a), (r - 5.5) * math.sin(a)
            p.setPen(QPen(MECH_STEEL_D, 0.7))
            p.setBrush(QBrush(MECH_STEEL_L))
            p.drawEllipse(QRectF(bx - 2.8, by - 2.8, 5.6, 5.6))
            sa = a + math.pi / 4
            p.setPen(QPen(MECH_STEEL_D, 0.6))
            p.drawLine(QLineF(bx - 1.6 * math.cos(sa), by - 1.6 * math.sin(sa),
                              bx + 1.6 * math.cos(sa), by + 1.6 * math.sin(sa)))
        # 轮缘内侧细刻线
        p.setPen(QPen(MECH_ROSE_D, 0.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(-r + 12, -r + 12, 2 * (r - 12), 2 * (r - 12)))
        # 圆盘钉（impulse jewel）：装在摆轮下侧、半径 pin_r 处，随摆轮/框架转并驱动擒纵叉
        # 局部坐标固定为 (pin_r·cos pin_base, pin_r·sin pin_base)，经 p.rotate(bal_ang) 后落在 pin 世界位置
        if pin is not None:
            dx = pin_r * math.cos(math.radians(pin_base))
            dy = pin_r * math.sin(math.radians(pin_base))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(MECH_STEEL_D))          # 圆盘底座
            p.drawEllipse(QRectF(dx - 4.5, dy - 4.5, 9, 9))
            p.setBrush(QBrush(MECH_RUBY))             # 红宝石钉
            p.drawEllipse(QRectF(dx - 2.6, dy - 2.6, 5.2, 5.2))
            p.setBrush(QBrush(MECH_STEEL_L))          # 高光
            p.drawEllipse(QRectF(dx - 1.0, dy - 1.0, 2.0, 2.0))
        p.restore()
        # 游丝（独立呼吸 + 外桩随框架公转）
        self.mm_hairspring(p, gx, gy, r, bal_ang - frame_ang, s, frame_ang)
        # 摆轮轴宝石
        self.mm_jewel(p, gx, gy, 4.2)

    def mm_hairspring(self, p, gx, gy, r, bal_ang, s, frame_ang=0.0):
        """游丝呼吸：阿基米德螺旋，内端随摆轮转、外端固定；摆动时螺距张合。
        frame_ang 为框架公转角：外桩/快慢针随框架转，内端跟随摆轮相对振荡。"""
        turns = 4.8
        n = 240
        r_in, r_out = 5.0, r * 0.66
        phi = math.radians(bal_ang)
        fa = math.radians(frame_ang)
        pts = []
        for i in range(n):
            u = i / (n - 1.0)
            base_ang = u * turns * 2.0 * math.pi - math.pi / 2.0
            base_r = r_in + u * (r_out - r_in)
            # 内端跟随摆轮(相对振荡)、外桩随框架公转：整体叠加 fa，再叠加随半径衰减的扭转
            ang = base_ang + fa + phi * (1.0 - u) ** 1.25
            # 呼吸：中部螺距随摆动相位张合（内外端半径固定）
            breath = 1.0 + 0.24 * s * math.sin(math.pi * u)
            rad = base_r * breath
            pts.append(QPointF(gx + rad * math.cos(ang), gy + rad * math.sin(ang)))
        poly = QPolygonF(pts)
        p.setPen(QPen(QColor(6, 10, 20, 225), 2.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(poly)
        p.setPen(QPen(QColor(162, 192, 244), 1.05))
        p.drawPolyline(poly)
        # 外桩（固定端）
        ex, ey = pts[-1].x(), pts[-1].y()
        p.setPen(QPen(MECH_ROSE_D, 1.0))
        p.setBrush(QBrush(MECH_ROSE))
        p.drawEllipse(QRectF(ex - 3.5, ey - 3.5, 7, 7))
        p.setPen(QPen(MECH_STEEL_L, 0.8))
        p.drawEllipse(QRectF(ex - 1.5, ey - 1.5, 3, 3))
        # 快慢针（regulator）：从摆轮轴伸向游丝外圈的杠杆 + 双夹片 + 调节螺钉
        ra = math.atan2(ey - gy, ex - gx)
        rlen = math.hypot(ex - gx, ey - gy)
        ux, uy = math.cos(ra), math.sin(ra)
        vx, vy = -uy, ux
        p.setPen(QPen(MECH_STEEL_D, 1.8))
        p.drawLine(QLineF(gx + 9 * ux, gy + 9 * uy,
                          gx + (rlen - 5) * ux, gy + (rlen - 5) * uy))
        for off in (-2.4, 2.4):
            fx = gx + (rlen - 7) * ux + off * vx
            fy = gy + (rlen - 7) * uy + off * vy
            p.setPen(QPen(MECH_STEEL_D, 0.6))
            p.setBrush(QBrush(MECH_STEEL_L))
            p.drawEllipse(QRectF(fx - 1.7, fy - 1.7, 3.4, 3.4))
        sx, sy = gx + (rlen - 13) * ux, gy + (rlen - 13) * uy
        p.setPen(QPen(MECH_ROSE_D, 0.7))
        p.setBrush(QBrush(MECH_ROSE))
        p.drawEllipse(QRectF(sx - 2.6, sy - 2.6, 5.2, 5.2))

    def mm_hands(self, p, cx, cy, local):
        """蓝钢剑形时分针（双切面）+ 玫瑰金扫动秒针 + 红宝石轴帽"""
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0
        edge = QColor(14, 18, 26, 235)
        hi_h, lo_h = QColor(232, 238, 248), QColor(150, 158, 176)
        hi_m, lo_m = QColor(126, 162, 228), QColor(48, 76, 138)

        def dauphine(angle_deg, length, width, back, hi, lo):
            a = math.radians(angle_deg - 90)
            ux, uy = math.cos(a), math.sin(a)
            vx, vy = -uy, ux
            tip = QPointF(cx + length * ux, cy + length * uy)
            root = QPointF(cx + back * ux, cy + back * uy)
            left = QPointF(root.x() + width * vx, root.y() + width * vy)
            right = QPointF(root.x() - width * vx, root.y() - width * vy)
            tail = QPointF(cx - back * 0.7 * ux, cy - back * 0.7 * uy)
            p.setPen(QPen(edge, 2.6))
            p.setBrush(QBrush(edge))
            p.drawPolygon(QPolygonF([tip, left, tail, right]))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(hi))
            p.drawPolygon(QPolygonF([tip, left, root]))
            p.setBrush(QBrush(lo))
            p.drawPolygon(QPolygonF([tip, right, root]))
            p.setPen(QPen(QColor(255, 255, 255, 190), 0.7))
            p.drawLine(QLineF(tip, root))

        dauphine(hour * 30, 86, 7.0, 16, hi_h, lo_h)
        dauphine(minute * 6, 124, 5.4, 18, hi_m, lo_m)
        # 扫动秒针
        a = math.radians(sec * 6 - 90)
        ux, uy = math.cos(a), math.sin(a)
        tail = QPointF(cx - 28 * ux, cy - 28 * uy)
        tip = QPointF(cx + 140 * ux, cy + 140 * uy)
        p.setPen(QPen(edge, 2.2))
        p.drawLine(QLineF(tail, tip))
        p.setPen(QPen(QColor(216, 154, 96), 1.5))
        p.drawLine(QLineF(tail, tip))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(216, 154, 96)))
        p.drawEllipse(QRectF(tail.x() - 4, tail.y() - 4, 8, 8))
        # 中心轴帽
        p.setPen(QPen(edge, 2))
        p.setBrush(QBrush(hi_h))
        p.drawEllipse(QRectF(cx - 8, cy - 8, 16, 16))
        self.mm_jewel(p, cx, cy, 3.6)


    # ================= 样式 6：天文机械腕表 =================
    def _build_astro_static(self):
        """预渲染天文腕表静态层（表壳/十二宫/时标/节气环/珐琅盘/副盘框/螺丝）"""
        dpr = 2
        pm = QPixmap(int(BASE * dpr), int(BASE * dpr))
        pm.fill(QColor(0, 0, 0, 0))
        sp = QPainter(pm)
        sp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        sp.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        sp.scale(dpr, dpr)
        cx = cy = 200.0
        self.astro_case(sp, cx, cy)
        self.astro_enamel(sp, cx, cy)
        self.astro_zodiac(sp, cx, cy)
        self.astro_markers(sp, cx, cy)
        self.astro_subdials(sp, cx, cy)
        self.astro_screws(sp, cx, cy)
        sp.end()
        return pm

    def paint_astro(self, p, ctx):
        cx = cy = 200.0
        local = ctx["local"]
        if self.astro_static is None:
            self.astro_static = self._build_astro_static()
        p.drawPixmap(QRectF(0, 0, BASE, BASE), self.astro_static,
                     QRectF(0, 0, self.astro_static.width(), self.astro_static.height()))
        # 动态：天文指示 + 齿轮 + 指针
        self.astro_zodiac_active(p, cx, cy, ctx["sun_lon"], ctx["zodiac_idx"])
        self.astro_sun_dial(p, cx, 100.0, ctx["sun_lon"])
        self.astro_moon_dial(p, cx, 300.0, ctx["elong"])
        self.astro_star_chart(p, cx, cy, ctx["lst"])
        self.astro_gears(p, cx, cy)
        self.astro_hands(p, cx, cy, local)

    def astro_case(self, p, cx, cy):
        """银钢表壳：锥形渐变模拟真实金属反光 + 玫瑰金倒角"""
        # 锥形渐变（明暗交替模拟抛光金属环绕反光）
        g = QConicalGradient(cx, cy, 18)
        stops = [
            (0.00, ASTRO_STEEL_D), (0.07, ASTRO_STEEL_L), (0.15, ASTRO_STEEL),
            (0.25, ASTRO_STEEL_L), (0.34, ASTRO_STEEL_D), (0.42, ASTRO_STEEL),
            (0.50, ASTRO_STEEL_L), (0.58, ASTRO_STEEL_D), (0.66, ASTRO_STEEL),
            (0.75, ASTRO_STEEL_L), (0.84, ASTRO_STEEL_D), (0.92, ASTRO_STEEL),
            (1.00, ASTRO_STEEL_D),
        ]
        for pos, col in stops:
            g.setColorAt(pos, col)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(cx - 196, cy - 196, 392, 392))
        # 内挖空，留出表圈宽度
        p.setBrush(QBrush(ASTRO_ENAMEL_D))
        p.drawEllipse(QRectF(cx - 182, cy - 182, 364, 364))
        # 玫瑰金倒角（线性渐变高光）
        bevel = QLinearGradient(cx - 180, cy - 180, cx + 180, cy + 180)
        bevel.setColorAt(0.0, ASTRO_ROSE_L)
        bevel.setColorAt(0.5, ASTRO_ROSE)
        bevel.setColorAt(1.0, ASTRO_ROSE_D)
        p.setPen(QPen(QBrush(bevel), 2.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - 180, cy - 180, 360, 360))
        p.setPen(QPen(ASTRO_ROSE_D, 1))
        p.drawEllipse(QRectF(cx - 176, cy - 176, 352, 352))
        # 表圈滚花
        for i in range(120):
            a = math.radians(i * 3)
            col = ASTRO_STEEL_L if i % 2 == 0 else ASTRO_STEEL_D
            p.setPen(QPen(col, 0.7))
            p.drawLine(QLineF(cx + 184 * math.cos(a), cy + 184 * math.sin(a),
                              cx + 194 * math.cos(a), cy + 194 * math.sin(a)))

    def astro_enamel(self, p, cx, cy):
        """深蓝珐琅主盘：径向渐变深邃感 + 太阳放射纹"""
        r = 176.0
        g = QRadialGradient(cx - 30, cy - 40, 30, cx, cy, r)
        g.setColorAt(0.0, QColor(34, 62, 100))
        g.setColorAt(0.55, ASTRO_ENAMEL)
        g.setColorAt(1.0, ASTRO_ENAMEL_D)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        # 太阳放射纹（细线从内向外）
        for i, jitter in enumerate(MECH_SUNBURST):
            a = math.radians(i * 1.5)
            col = QColor(60, 92, 138, 90) if i % 3 == 0 else QColor(30, 54, 88, 70)
            p.setPen(QPen(col, 0.7))
            p.drawLine(QLineF(cx + 50 * math.cos(a), cy + 50 * math.sin(a),
                              cx + 174 * math.cos(a), cy + 174 * math.sin(a)))
        p.setPen(QPen(ASTRO_ROSE_D, 0.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))

    def astro_zodiac(self, p, cx, cy):
        """黄道十二宫环：12 径向分隔 + 星座中文名（静态，高亮另画）"""
        r_out, r_in = 174.0, 148.0
        r_mid = (r_out + r_in) / 2.0
        # 只画环带（粗笔描边中径圆），保留盘内珐琅太阳纹
        p.setPen(QPen(QBrush(ASTRO_ENAMEL), int(r_out - r_in)))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_mid, cy - r_mid, 2 * r_mid, 2 * r_mid))
        # 12 条径向分隔线（只画在环带内，不穿过盘心）
        for i in range(12):
            a = math.radians(i * 30 - 90 - 15)
            p.setPen(QPen(ASTRO_ROSE_D, 0.8))
            p.drawLine(QLineF(cx + r_in * math.cos(a), cy + r_in * math.sin(a),
                              cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
        for i, name in enumerate(ZODIACS):
            am = math.radians(i * 30 - 90)
            p.setFont(self.font_cn)
            p.setPen(QPen(ASTRO_TEXT))
            tx = cx + (r_in + r_out) / 2 * math.cos(am)
            ty = cy + (r_in + r_out) / 2 * math.sin(am)
            p.drawText(QRectF(tx - 17, ty - 10, 34, 20), Qt.AlignmentFlag.AlignCenter, name)
        p.setPen(QPen(ASTRO_ROSE, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_out, cy - r_out, 2 * r_out, 2 * r_out))
        p.drawEllipse(QRectF(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in))

    def astro_zodiac_active(self, p, cx, cy, sun_lon, idx):
        """当前星座玫瑰金高亮弧带 + 金色黄经指示针"""
        r_out, r_in = 174.0, 148.0
        r_mid = (r_out + r_in) / 2.0
        rect = QRectF(cx - r_mid, cy - r_mid, 2 * r_mid, 2 * r_mid)
        # 用粗画笔沿中径画弧，等效一段环带，避免 arcTo 路径问题
        p.setPen(QPen(QColor(206, 158, 104, 80), int(r_out - r_in)))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, int((idx * 30 - 90 - 13) * 16), int(26 * 16))
        # 黄经精确指示针
        a = math.radians(sun_lon - 90)
        p.setPen(QPen(ASTRO_GOLD, 2.2))
        p.drawLine(QLineF(cx + 149 * math.cos(a), cy + 149 * math.sin(a),
                          cx + 173 * math.cos(a), cy + 173 * math.sin(a)))

    def astro_markers(self, p, cx, cy):
        """立体玫瑰金时标（亮暗切面）+ 分钟轨道 + 24 节气刻度"""
        # 分钟轨道
        for i in range(60):
            a = math.radians(i * 6 - 90)
            major = (i % 5 == 0)
            r1 = 143 if major else 146
            p.setPen(QPen(ASTRO_ROSE if major else ASTRO_STEEL_D, 1.2 if major else 0.6))
            p.drawLine(QLineF(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                              cx + 148 * math.cos(a), cy + 148 * math.sin(a)))
        # 立体时标（12 个，菱形切面）
        for h in range(12):
            a = math.radians(h * 30 - 90)
            ux, uy = math.cos(a), math.sin(a)
            vx, vy = -uy, ux
            ro, ri, w = 142.0, 130.0, 3.2
            tip = (cx + ri * ux, cy + ri * uy)
            lo = (cx + ro * ux + w * vx, cy + ro * uy + w * vy)
            rop = (cx + ro * ux - w * vx, cy + ro * uy - w * vy)
            # 主位时标加长加宽
            if h % 3 == 0:
                ri, w = 126.0, 4.6
                tip = (cx + ri * ux, cy + ri * uy)
                lo = (cx + ro * ux + w * vx, cy + ro * uy + w * vy)
                rop = (cx + ro * ux - w * vx, cy + ro * uy - w * vy)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(ASTRO_ROSE_L))
            p.drawPolygon(QPolygonF([QPointF(cx + ro * ux, cy + ro * uy),
                                     QPointF(*lo), QPointF(*tip)]))
            p.setBrush(QBrush(ASTRO_ROSE_D))
            p.drawPolygon(QPolygonF([QPointF(cx + ro * ux, cy + ro * uy),
                                     QPointF(*rop), QPointF(*tip)]))
        # 24 节气刻度环
        for i in range(24):
            a = math.radians(i * 15 - 90)
            major = (i % 6 == 0)
            r1 = 122 if major else 125
            p.setPen(QPen(ASTRO_GOLD if major else ASTRO_ROSE_D, 1.0 if major else 0.5))
            p.drawLine(QLineF(cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                              cx + 128 * math.cos(a), cy + 128 * math.sin(a)))

    def astro_subdials(self, p, cx, cy):
        """副盘静态框：太阳盘（上）/ 月相窗（下）/ 星盘（中）/ 齿轮座"""
        # 太阳黄道盘
        sy = 100.0
        p.setPen(QPen(ASTRO_ROSE, 1.4))
        p.setBrush(QBrush(ASTRO_ENAMEL_D))
        p.drawEllipse(QRectF(cx - 26, sy - 26, 52, 52))
        p.setPen(QPen(ASTRO_ROSE_D, 0.7))
        p.drawEllipse(QRectF(cx - 20, sy - 20, 40, 40))
        for i in range(12):
            a = math.radians(i * 30 - 90)
            p.setPen(QPen(ASTRO_ROSE_D, 0.7))
            p.drawLine(QLineF(cx + 21 * math.cos(a), sy + 21 * math.sin(a),
                              cx + 25 * math.cos(a), sy + 25 * math.sin(a)))
        # 月相窗
        my = 300.0
        p.setPen(QPen(ASTRO_ROSE, 1.4))
        p.setBrush(QBrush(QColor(8, 18, 36)))
        p.drawEllipse(QRectF(cx - 30, my - 30, 60, 60))
        p.setPen(QPen(ASTRO_ROSE_D, 0.7))
        p.drawEllipse(QRectF(cx - 25, my - 25, 50, 50))
        # 星盘外框
        p.setPen(QPen(ASTRO_ROSE, 1.2))
        p.setBrush(QBrush(ASTRO_ENAMEL_D))
        p.drawEllipse(QRectF(cx - 46, cy - 46, 92, 92))
        p.setPen(QPen(ASTRO_ROSE_D, 0.7))
        p.drawEllipse(QRectF(cx - 42, cy - 42, 84, 84))
        # 齿轮座暗窝
        for gx, gy in [(cx - 62, cy), (cx + 62, cy)]:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(ASTRO_ENAMEL_D))
            p.drawEllipse(QRectF(gx - 19, gy - 19, 38, 38))

    def astro_screws(self, p, cx, cy):
        for ang, dist in [(45, 116), (135, 116), (225, 116), (315, 116)]:
            a = math.radians(ang)
            gx, gy = cx + dist * math.cos(a), cy + dist * math.sin(a)
            r = 4
            p.setPen(QPen(ASTRO_STEEL_D, 0.8))
            p.setBrush(QBrush(ASTRO_STEEL))
            p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))
            slot = math.radians(ang + 45)
            p.setPen(QPen(ASTRO_ENAMEL_D, 1.3))
            p.drawLine(QLineF(gx - r * 0.7 * math.cos(slot), gy - r * 0.7 * math.sin(slot),
                              gx + r * 0.7 * math.cos(slot), gy + r * 0.7 * math.sin(slot)))

    def astro_sun_dial(self, p, gx, gy, sun_lon):
        """金色太阳按当前黄经在盘内运行"""
        a = math.radians(sun_lon - 90)
        ox, oy = gx + 15 * math.cos(a), gy + 15 * math.sin(a)
        g = QRadialGradient(ox - 2, oy - 2, 1, ox, oy, 7)
        g.setColorAt(0.0, QColor(255, 246, 210))
        g.setColorAt(0.6, ASTRO_GOLD)
        g.setColorAt(1.0, QColor(160, 120, 40))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(ox - 7, oy - 7, 14, 14))
        # 光芒
        for k in range(8):
            b = math.radians(k * 45 + sun_lon)
            p.setPen(QPen(ASTRO_GOLD, 0.8))
            p.drawLine(QLineF(ox + 9 * math.cos(b), oy + 9 * math.sin(b),
                              ox + 13 * math.cos(b), oy + 13 * math.sin(b)))

    def astro_moon_dial(self, p, cx, cy, elong):
        """真实月相：按日月黄经差画明暗界线"""
        r = 24.0
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(6, 14, 30)))
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        waxing = elong < 180.0
        c = math.cos(math.radians(elong))
        steps = 48
        pts = []
        for i in range(steps + 1):
            y = -r + 2 * r * i / steps
            w = math.sqrt(max(0.0, r * r - y * y))
            x0 = c * w if waxing else -w
            pts.append((cx + x0, cy + y))
        for i in range(steps, -1, -1):
            y = -r + 2 * r * i / steps
            w = math.sqrt(max(0.0, r * r - y * y))
            x1 = w if waxing else -c * w
            pts.append((cx + x1, cy + y))
        p.setBrush(QBrush(ASTRO_MOON))
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
        # 点缀星
        for dx, dy, s in [(-14, -8, 1.2), (13, -11, 1), (15, 9, 1.3), (-12, 10, 1)]:
            p.setBrush(QBrush(ASTRO_TEXT))
            p.drawEllipse(QRectF(cx + dx - s, cy + dy - s, 2 * s, 2 * s))

    def astro_star_chart(self, p, cx, cy, lst):
        """恒星时驱动旋转的星盘"""
        r = 40.0
        p.save()
        p.translate(cx, cy)
        p.rotate(lst)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(ASTRO_STEEL_L))
        for ang, rad_norm, size in STAR_POINTS:
            rad = rad_norm * (r - 4)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            p.drawEllipse(QRectF(x - size * 0.6, y - size * 0.6, size * 1.2, size * 1.2))
        # 黄道十字
        p.setPen(QPen(ASTRO_ROSE, 0.7))
        p.drawLine(QLineF(-r + 4, 0, r - 4, 0))
        p.drawLine(QLineF(0, -r + 4, 0, r - 4))
        p.restore()
        # 中心红宝石
        self.astro_jewel(p, cx, cy, 4)

    def astro_gears(self, p, cx, cy):
        """两侧玫瑰金咬合齿轮（真实齿形 + 红宝石轴承）"""
        for gx, gy, r, teeth in [(cx - 62, cy, 16, 16), (cx + 62, cy, 16, 16)]:
            pts = []
            for i in range(teeth * 2):
                a = math.radians(i * 180.0 / teeth)
                rr = r if i % 2 == 0 else r * 0.84
                pts.append(QPointF(gx + rr * math.cos(a), gy + rr * math.sin(a)))
            p.setPen(QPen(ASTRO_ROSE_D, 0.6))
            p.setBrush(QBrush(ASTRO_ROSE))
            p.drawPolygon(QPolygonF(pts))
            p.setPen(QPen(ASTRO_ROSE_L, 0.8))
            p.setBrush(QBrush(ASTRO_ENAMEL))
            p.drawEllipse(QRectF(gx - 10, gy - 10, 20, 20))
            for k in range(4):
                a = math.radians(k * 90)
                p.setPen(QPen(ASTRO_ROSE, 1.8))
                p.drawLine(QLineF(gx + 3 * math.cos(a), gy + 3 * math.sin(a),
                                  gx + 10 * math.cos(a), gy + 10 * math.sin(a)))
            self.astro_jewel(p, gx, gy, 3)

    def astro_jewel(self, p, gx, gy, r):
        p.setPen(QPen(ASTRO_ROSE, 1))
        p.setBrush(QBrush(ASTRO_ROSE_D))
        p.drawEllipse(QRectF(gx - r - 1.5, gy - r - 1.5, 2 * (r + 1.5), 2 * (r + 1.5)))
        g = QRadialGradient(gx - r * 0.3, gy - r * 0.3, 0.5, gx, gy, r)
        g.setColorAt(0.0, QColor(255, 130, 145))
        g.setColorAt(1.0, ASTRO_RUBY)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(gx - r, gy - r, 2 * r, 2 * r))

    def astro_hands(self, p, cx, cy, local):
        """蓝钢剑形时分针（双色切面 + 中脊高光）+ 玫瑰金秒针"""
        sec = local.second + local.microsecond / 1e6
        minute = local.minute + sec / 60.0
        hour = (local.hour % 12) + minute / 60.0

        def dauphine(angle_deg, length, width, back):
            a = math.radians(angle_deg - 90)
            ux, uy = math.cos(a), math.sin(a)
            vx, vy = -uy, ux
            tip = (cx + length * ux, cy + length * uy)
            base = (cx + back * ux, cy + back * uy)
            left = (base[0] + width * vx, base[1] + width * vy)
            right = (base[0] - width * vx, base[1] - width * vy)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(ASTRO_BLUE_L))
            p.drawPolygon(QPolygonF([QPointF(*tip), QPointF(*left), QPointF(*base)]))
            p.setBrush(QBrush(ASTRO_BLUE))
            p.drawPolygon(QPolygonF([QPointF(*tip), QPointF(*right), QPointF(*base)]))
            p.setPen(QPen(QColor(150, 185, 240), 0.6))
            p.drawLine(QLineF(tip[0], tip[1], base[0], base[1]))

        dauphine(hour * 30, 80, 6.5, 15)
        dauphine(minute * 6, 118, 5.0, 17)
        # 玫瑰金秒针
        a = math.radians(sec * 6 - 90)
        pen = QPen(ASTRO_ROSE, 1.3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(cx - 16 * math.cos(a), cy - 16 * math.sin(a),
                          cx + 124 * math.cos(a), cy + 124 * math.sin(a)))
        # 中心宝石帽
        p.setPen(QPen(ASTRO_ROSE_D, 1))
        p.setBrush(QBrush(ASTRO_ROSE))
        p.drawEllipse(QRectF(cx - 6, cy - 6, 12, 12))
        self.astro_jewel(p, cx, cy, 3.2)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    clock = AstroClock()
    clock.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
