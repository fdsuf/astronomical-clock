# -*- coding: utf-8 -*-
"""候选功能效果图：不修改主程序，仅离屏渲染样例副盘 + 推荐组合装盘效果。"""
import os, sys, math
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, '.')
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QFontDatabase, QFont, QColor, QPen, QBrush, QPolygonF, QConicalGradient
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
from datetime import datetime, timezone
import astronomical_clock as ac

app = QApplication(sys.argv)
for fp in ['C:/Windows/Fonts/georgia.ttf', 'C:/Windows/Fonts/georgiab.ttf',
           'C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/times.ttf',
           'C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf']:
    if os.path.exists(fp):
        QFontDatabase.addApplicationFont(fp)

M = ac.MECH_ROSE
D = ac.MECH_ROSE_D
SL = ac.MECH_STEEL_L
SD = ac.MECH_STEEL_D
TXT = ac.MECH_TEXT
RUBY = ac.MECH_RUBY
BLUE = ac.MECH_BLUE_L

f_title = QFont('Microsoft YaHei', 15)
f_title.setBold(True)
f_sub = QFont('Microsoft YaHei', 9)
f_cn = QFont('Microsoft YaHei', 10)
f_cn.setBold(True)
f_num = QFont('Georgia', 9)
f_num.setBold(True)


def jewel(p, x, y, r):
    p.setPen(QPen(D, 0.6))
    p.setBrush(QBrush(RUBY))
    p.drawEllipse(QRectF(x - r, y - r, 2 * r, 2 * r))
    p.setPen(QPen(QColor(255, 180, 180), 0.5))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(x - r * 0.4 - 0.5, y - r * 0.4 - 0.5, r * 0.8, r * 0.8))


def label_plate(p, cx, cy, r, text):
    """与现有 MOON/POWER 一致的深色圆角标签底衬"""
    lr = QRectF(cx - 26, cy + r - 1, 52, 12)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(10, 12, 18, 205)))
    p.drawRoundedRect(lr, 3, 3)
    p.setFont(f_sub)
    p.setPen(QPen(SL))
    p.drawText(lr, Qt.AlignmentFlag.AlignCenter, text)


def base(p, cx, cy, r, label):
    p.setPen(QPen(D, 1.3))
    p.setBrush(QBrush(QColor(14, 17, 24)))
    p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
    p.setPen(QPen(SL, 0.7))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx - r + 2.2, cy - r + 2.2, 2 * (r - 2.2), 2 * (r - 2.2)))
    p.setPen(QPen(D, 0.5))
    p.drawEllipse(QRectF(cx - r + 5, cy - r + 5, 2 * (r - 5), 2 * (r - 5)))


def needle(p, cx, cy, ang_deg, length, color, w=1.8, tail=4):
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    pen = QPen(color, w)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QLineF(cx - tail * ux, cy - tail * uy,
                      cx + length * ux, cy + length * uy))


# ---------- 候选 1：二十四节气盘 ----------
def solar_term(p, cx, cy, r, sun_lon):
    base(p, cx, cy, r, '')
    term, prog = ac.solar_term_info(sun_lon)
    idx = int(sun_lon // 15.0) % 24
    for k in range(24):
        a = math.radians(k * 15 - 90)
        major = k % 6 == 0
        ro = r - 3.5
        ri = ro - (4 if major else 2.2)
        p.setPen(QPen(ac.MECH_ROSE.lighter(150) if k == idx else (SL if major else SD),
                      1.4 if k == idx else (0.9 if major else 0.5)))
        p.drawLine(QLineF(cx + ri * math.cos(a), cy + ri * math.sin(a),
                          cx + ro * math.cos(a), cy + ro * math.sin(a)))
    a = math.radians((idx + prog) * 15 - 90)
    needle(p, cx, cy, math.degrees(a) + 90, r - 9, M, 2.0)
    jewel(p, cx, cy, 2.6)
    p.setFont(f_sub)
    p.setPen(QPen(TXT))
    p.drawText(QRectF(cx - r + 3, cy + r * 0.32, 2 * r - 6, 12),
               Qt.AlignmentFlag.AlignCenter, term)
    label_plate(p, cx, cy, r, '节气')


# ---------- 候选 2：黄道十二宫盘 ----------
def zodiac(p, cx, cy, r, sun_lon):
    base(p, cx, cy, r, '')
    zi = int(sun_lon // 30.0) % 12
    for k in range(12):
        a = math.radians(k * 30 - 90)
        major = (k == zi)
        ro = r - 3.0
        ri = ro - (4.5 if major else 2.5)
        p.setPen(QPen(M if major else SL, 1.6 if major else 0.8))
        p.drawLine(QLineF(cx + ri * math.cos(a), cy + ri * math.sin(a),
                          cx + ro * math.cos(a), cy + ro * math.sin(a)))
    for k in (0, 3, 6, 9):
        a = math.radians(k * 30 - 90)
        tx, ty = cx + (r - 11) * math.cos(a), cy + (r - 11) * math.sin(a)
        p.setFont(f_num)
        p.setPen(QPen(SD))
        p.drawText(QRectF(tx - 9, ty - 7, 18, 14), Qt.AlignmentFlag.AlignCenter,
                   ac.ROMAN[k])
    a = math.radians(zi * 30 - 90)
    sx, sy = cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a)
    p.setPen(QPen(QColor(255, 210, 120), 0.6))
    p.setBrush(QBrush(QColor(240, 190, 90)))
    p.drawEllipse(QRectF(sx - 3, sy - 3, 6, 6))
    p.setFont(f_sub)
    p.setPen(QPen(TXT))
    p.drawText(QRectF(cx - r + 3, cy + r * 0.32, 2 * r - 6, 12),
               Qt.AlignmentFlag.AlignCenter, ac.ZODIACS[zi])
    jewel(p, cx, cy, 2.4)
    label_plate(p, cx, cy, r, '星宫')


# ---------- 候选 3：恒星时盘 ----------
def sidereal(p, cx, cy, r, lst_deg):
    base(p, cx, cy, r, '')
    for k in range(24):
        a = math.radians(k * 15 - 90)
        major = k % 6 == 0
        ro = r - 3.5
        ri = ro - (4 if major else 2)
        p.setPen(QPen(SL if major else SD, 0.9 if major else 0.5))
        p.drawLine(QLineF(cx + ri * math.cos(a), cy + ri * math.sin(a),
                          cx + ro * math.cos(a), cy + ro * math.sin(a)))
    for k, h in enumerate((0, 6, 12, 18)):
        a = math.radians(k * 90 - 90)
        tx, ty = cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a)
        p.setFont(f_num)
        p.setPen(QPen(SD))
        p.drawText(QRectF(tx - 8, ty - 6, 16, 12), Qt.AlignmentFlag.AlignCenter, str(h))
    needle(p, cx, cy, lst_deg - 90 + 90, r - 9, BLUE, 1.8)
    jewel(p, cx, cy, 2.4)
    p.setFont(f_sub)
    p.setPen(QPen(TXT))
    p.drawText(QRectF(cx - r, cy + r * 0.35, 2 * r, 13), Qt.AlignmentFlag.AlignCenter,
               '%.1fh' % ((lst_deg % 360.0) / 15.0))
    label_plate(p, cx, cy, r, '恒星时')


# ---------- 候选 4：月龄数字 ----------
def moon_age(p, cx, cy, r, elong):
    base(p, cx, cy, r, '')
    age = (elong / 360.0) * 29.53
    mr = r - 11
    waxing = elong < 180.0
    c = math.cos(math.radians(elong))
    pts = []
    steps = 30
    for i in range(steps + 1):
        y = -mr + 2 * mr * i / steps
        w = math.sqrt(max(0.0, mr * mr - y * y))
        pts.append(QPointF(cx + (c * w if waxing else -w), cy - 4 + y))
    for i in range(steps, -1, -1):
        y = -mr + 2 * mr * i / steps
        w = math.sqrt(max(0.0, mr * mr - y * y))
        pts.append(QPointF(cx + (w if waxing else -c * w), cy - 4 + y))
    p.setPen(QPen(D, 0.5))
    p.setBrush(QBrush(ac.ASTRO_MOON))
    p.drawPolygon(QPolygonF(pts))
    p.setFont(f_num)
    p.setPen(QPen(M))
    p.drawText(QRectF(cx - r, cy + r * 0.45, 2 * r, 14), Qt.AlignmentFlag.AlignCenter,
               'D%.0f' % age)
    label_plate(p, cx, cy, r, '月龄')


# ---------- 候选 5：星期日期窗 ----------
def date_window(p, cx, cy, r, local):
    base(p, cx, cy, r, '')
    wk = ['一', '二', '三', '四', '五', '六', '日'][local.weekday()]
    w, h = 2 * r - 12, 16
    win = QRectF(cx - w / 2, cy - h / 2 - 3, w, h)
    p.setPen(QPen(D, 1.0))
    p.setBrush(QBrush(QColor(8, 10, 15)))
    p.drawRoundedRect(win, 2, 2)
    p.setFont(f_cn)
    p.setPen(QPen(M))
    p.drawText(win, Qt.AlignmentFlag.AlignCenter, '周%s  %d日' % (wk, local.day))
    p.setFont(f_num)
    p.setPen(QPen(SD))
    p.drawText(QRectF(cx - r, cy + r * 0.42, 2 * r, 13), Qt.AlignmentFlag.AlignCenter,
               local.strftime('%b'))
    label_plate(p, cx, cy, r, '日期')


# ---------- 候选 6：小秒盘 ----------
def small_seconds(p, cx, cy, r, sec):
    base(p, cx, cy, r, '')
    for k in range(60):
        a = math.radians(k * 6 - 90)
        major = k % 5 == 0
        ro = r - 3.2
        ri = ro - (3.5 if major else 1.8)
        p.setPen(QPen(SL if major else SD, 0.9 if major else 0.45))
        p.drawLine(QLineF(cx + ri * math.cos(a), cy + ri * math.sin(a),
                          cx + ro * math.cos(a), cy + ro * math.sin(a)))
    needle(p, cx, cy, sec * 6 - 90 + 90, r - 8, RUBY, 1.6, tail=5)
    jewel(p, cx, cy, 2.2)
    label_plate(p, cx, cy, r, '小秒')


# ---------- 候选 7：两地时 GMT ----------
def gmt(p, cx, cy, r, local):
    base(p, cx, cy, r, '')
    for k in range(24):
        a = math.radians(k * 15 - 90)
        major = k % 6 == 0
        ro = r - 3.2
        ri = ro - (3.5 if major else 1.8)
        p.setPen(QPen(SL if major else SD, 0.9 if major else 0.45))
        p.drawLine(QLineF(cx + ri * math.cos(a), cy + ri * math.sin(a),
                          cx + ro * math.cos(a), cy + ro * math.sin(a)))
    hour = (local.hour % 12) / 12.0 * 360.0 - 90 + 90
    needle(p, cx, cy, hour, r - 10, M, 2.0, tail=4)
    gmt_hour = ((local.hour + 8) % 24) / 24.0 * 360.0 - 90 + 90
    needle(p, cx, cy, gmt_hour, r - 7, BLUE, 1.5, tail=4)
    jewel(p, cx, cy, 2.2)
    p.setFont(f_sub)
    p.setPen(QPen(SD))
    p.drawText(QRectF(cx - r, cy + r * 0.42, 2 * r, 13), Qt.AlignmentFlag.AlignCenter,
               'GMT+8')
    label_plate(p, cx, cy, r, '两地时')


# ---------- 候选 8：昼夜指示 ----------
def daynight(p, cx, cy, r, local):
    base(p, cx, cy, r, '')
    hr = local.hour + local.minute / 60.0
    day = 6.0 <= hr < 18.0
    g = QConicalGradient(cx, cy, -90)
    g.setColorAt(0.0, QColor(240, 190, 90))
    g.setColorAt(0.5, QColor(240, 190, 90))
    g.setColorAt(0.5, QColor(40, 55, 95))
    g.setColorAt(1.0, QColor(40, 55, 95))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(g))
    p.drawEllipse(QRectF(cx - r + 6, cy - r + 6, 2 * (r - 6), 2 * (r - 6)))
    p.setPen(QPen(D, 0.6))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx - r + 6, cy - r + 6, 2 * (r - 6), 2 * (r - 6)))
    needle(p, cx, cy, hr / 24.0 * 360.0 - 90 + 90, r - 8, RUBY, 2.0)
    jewel(p, cx, cy, 2.2)
    p.setFont(f_cn)
    p.setPen(QPen(QColor(240, 190, 90) if day else ac.MECH_STEEL_L))
    p.drawText(QRectF(cx - r, cy + r * 0.42, 2 * r, 13), Qt.AlignmentFlag.AlignCenter,
               '昼' if day else '夜')
    label_plate(p, cx, cy, r, '昼夜')


# ============ 图 1：候选样例目录 ============
now = datetime.now()
now_utc = datetime.now(timezone.utc)
jd = ac.julian_day(now_utc)
sun_lon = ac.sun_apparent_longitude(jd)
elong = ac.moon_elongation(jd)
lst = ac.local_sidereal_degrees(jd, 120.0)   # 度数 0-360
lst_h = (lst / 15.0) % 24.0                   # 换算成小时 0-24

W, H = 1240, 900
pm = QPixmap(W, H)
pm.fill(QColor(18, 20, 26))
p = QPainter(pm)
p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

p.setFont(f_title)
p.setPen(QPen(QColor(240, 232, 218)))
p.drawText(QRectF(0, 18, W, 30), Qt.AlignmentFlag.AlignCenter, '机械表盘 · 可新增功能候选样例')
p.setFont(f_sub)
p.setPen(QPen(QColor(150, 150, 158)))
p.drawText(QRectF(0, 50, W, 20), Qt.AlignmentFlag.AlignCenter,
           '所有样例沿用现有表盘的玫瑰金/拉丝钢/红宝石配色；第一档为真实天文数据驱动')

items = [
    ('① 二十四节气盘', '真数据 solar_term_info', solar_term, (sun_lon,), ac.SOLAR_TERMS[int(sun_lon // 15) % 24]),
    ('② 黄道十二宫盘', '真数据 zodiac_idx', zodiac, (sun_lon,), ac.ZODIACS[int(sun_lon // 30) % 12]),
    ('③ 恒星时盘', '真数据 local sidereal', sidereal, (lst,), '%.1fh' % lst_h),
    ('④ 月龄显示', '真数据 elong', moon_age, (elong,), 'D%.0f' % ((elong / 360.0) * 29.53)),
    ('⑤ 星期日期窗', '真实日期', date_window, (now,), '%d日' % now.day),
    ('⑥ 小秒盘', '真实秒', small_seconds, (now.second,), '秒'),
    ('⑦ 两地时 GMT', '本地+8区', gmt, (now,), 'GMT+8'),
    ('⑧ 昼夜指示', '真实时间', daynight, (now,), '昼' if 6 <= now.hour < 18 else '夜'),
]

cols, rows = 4, 2
cw, ch = W // cols, 340
r = 62
for i, (name, src, fn, args, val) in enumerate(items):
    col, row = i % cols, i // cols
    bx = col * cw
    by = 92 + row * ch
    p.setFont(f_cn)
    p.setPen(QPen(QColor(230, 226, 216)))
    p.drawText(QRectF(bx, by, cw, 24), Qt.AlignmentFlag.AlignCenter, name)
    p.setFont(f_sub)
    p.setPen(QPen(QColor(150, 160, 175)))
    p.drawText(QRectF(bx, by + 24, cw, 18), Qt.AlignmentFlag.AlignCenter, src)
    cx, cy = bx + cw / 2, by + 56 + r
    fn(p, cx, cy, r, *args)
    p.setFont(f_sub)
    p.setPen(QPen(ac.MECH_ROSE.lighter(150)))
    p.drawText(QRectF(bx, by + 56 + 2 * r + 10, cw, 18), Qt.AlignmentFlag.AlignCenter,
               '当前: ' + str(val))

p.end()
pm.save('_cand_catalog.png')
print('saved _cand_catalog.png')

# ============ 图 2：推荐组合装盘效果 ============
w = ac.AstroClock()
w.timer.stop()
try:
    w.locator.quit()
    w.locator.wait(500)
except Exception:
    pass
w.set_theme('mechanical')
w._warm_up()
ctx = {'jd': jd, 'sun_lon': sun_lon, 'elong': elong, 'lst': lst,
       'term': ac.solar_term_info(sun_lon)[0], 'term_prog': ac.solar_term_info(sun_lon)[1],
       'zodiac_idx': int(sun_lon // 30.0) % 12, 'local': now}

S = 1200
pm2 = QPixmap(S, S)
pm2.fill(QColor(16, 18, 23))
p2 = QPainter(pm2)
p2.setRenderHint(QPainter.RenderHint.Antialiasing, True)
p2.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
p2.scale(S / ac.BASE, S / ac.BASE)
w.paint_mechanical(p2, ctx)

sr = ac.SUB_R
solar_term(p2, 135, 135, sr, sun_lon)
zodiac(p2, 265, 270, sr, sun_lon)
p2.end()
pm2.save('_cand_on_dial.png')
print('saved _cand_on_dial.png')
