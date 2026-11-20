# -*- coding: utf-8 -*-
"""外圈动效效果图 v2：局部放大改为极坐标展开（角度→横向，半径→纵向），
环带效果一目了然。不改主程序，全部离屏渲染。

径向实测定位（500px 基准）：
  r151-172  干净暗底（罗马字墨迹约 155-165）
  r173-180  分钟刻度
  r181-185  玫瑰金倒角环 RGB(180,135,96)
  r187-196  滚花刻线
"""
import os
import sys
import math

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, '.')

import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import (QPixmap, QPainter, QFontDatabase, QColor, QPen,
                         QBrush, QRadialGradient, QPainterPath)
from PyQt6.QtCore import Qt, QRectF, QLineF
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

import astronomical_clock as ac

app = QApplication(sys.argv)
for fp in ['C:/Windows/Fonts/georgia.ttf', 'C:/Windows/Fonts/georgiab.ttf',
           'C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/times.ttf',
           'C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/msyhbd.ttc',
           'C:/Windows/Fonts/msjh.ttc', 'C:/Windows/Fonts/msjhbd.ttc']:
    if os.path.exists(fp):
        QFontDatabase.addApplicationFont(fp)

w = ac.AstroClock()
w.timer.stop()
try:
    w.locator.quit()
    w.locator.wait(500)
except Exception:
    pass
w.set_theme('mechanical')
w._warm_up()

LOCAL = datetime(2026, 11, 20, 12, 57, 25)
LAT = 30.0
EPS = math.radians(23.4397)
_lon = math.radians(ac.sun_apparent_longitude(ac.julian_day(LOCAL.replace(tzinfo=timezone.utc))))
_dec = math.asin(math.sin(EPS) * math.sin(_lon))
H0 = math.degrees(math.acos(max(-1.0, min(1.0, -math.tan(math.radians(LAT)) * math.tan(_dec)))))
DAYLEN = 2.0 * H0 / 15.0
SUNRISE, SUNSET = 12.0 - DAYLEN / 2.0, 12.0 + DAYLEN / 2.0


def ctx_of(local):
    jd = ac.julian_day(local.replace(tzinfo=timezone.utc))
    sun = ac.sun_apparent_longitude(jd)
    term, prog = ac.solar_term_info(sun)
    return {'jd': jd, 'sun_lon': sun, 'elong': ac.moon_elongation(jd),
            'lst': ac.local_sidereal_degrees(jd, 120.0), 'term': term,
            'term_prog': prog, 'zodiac_idx': int(sun // 30) % 12, 'local': local}


CTX = ctx_of(LOCAL)
YEAR_R = 170.4


def fx_second_glow(p, cx, cy, local, ctx):
    sec = local.second + local.microsecond / 1e6
    for k in range(11, 0, -1):
        s = sec - k
        if s < 0:
            continue
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
    pen = QPen(QColor(255, 242, 212), 2.3)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(QLineF(cx + 171.8 * math.cos(a), cy + 171.8 * math.sin(a),
                      cx + 180.4 * math.cos(a), cy + 180.4 * math.sin(a)))


def fx_day_night(p, cx, cy, local, ctx):
    """② 昼夜弧：玫瑰金环按日出/日落分段——昼=亮金，夜=深蓝，交界放日/月标记。
    注意：drawArc 的笔宽以「框半径」为中线，故框半径须取 (r_out+r_in)/2，
    否则弧带会整体外移（实测 r_out 作框半径时会落到 183.7~187.1）。"""
    r_out, r_in = 185.0, 181.4
    r_mid = (r_out + r_in) / 2.0
    wdt = r_out - r_in
    rect = QRectF(cx - r_mid, cy - r_mid, 2 * r_mid, 2 * r_mid)

    def qt_ang(hour):
        return 90.0 - ((hour - 12.0) / 24.0) * 360.0

    # 夜：整圈先铺暗调玫瑰金（不用蓝色——会抢掉整体金调，显得突兀）
    pen = QPen(QColor(74, 64, 62), wdt)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(rect)
    # 昼：从日出顺时针扫到日落，暖亮金
    # 跨度必须用「角度差」直接算：qt_ang 随小时递减，qt_ang(SUNSET)-qt_ang(SUNRISE) 本身已是负值。
    # 若套 %360 会把 -156° 变成 +204°（昼长 10.4h 被画成 13.6h）。
    a0, a1 = qt_ang(SUNRISE), qt_ang(SUNSET)
    pen = QPen(QColor(246, 208, 156), wdt)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(rect, int(a0 * 16), int((a1 - a0) * 16))
    # 交界标记：qt_ang 已是 Qt 角（0=3点、90=12点，逆时针），
    # 转成数学坐标须 x=cos、y=-sin，不能再减 90。
    for hour, is_sun in ((SUNRISE, True), (SUNSET, False)):
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


def fx_case_glint(p, cx, cy, local, ctx):
    """③ 表壳光泽流转：一道光带绕壳照亮滚花刻线，峰值亮度明显。
    光晕须裁到表壳圆（r=196）内，否则径向渐变会溢出表盘外形成白团。"""
    sweep = (local.timestamp() * 15.0) % 360.0
    for i in range(180):
        ang = i * 2.0
        d = abs((ang - sweep + 180.0) % 360.0 - 180.0)
        if d > 70.0:
            continue
        k = math.cos(math.radians(d / 70.0 * 90.0)) ** 1.7
        alpha = int(240 * k)
        if alpha <= 5:
            continue
        a = math.radians(ang)
        pen = QPen(QColor(255, 250, 240, alpha), 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(cx + 187.0 * math.cos(a), cy + 187.0 * math.sin(a),
                          cx + 195.6 * math.cos(a), cy + 195.6 * math.sin(a)))
    # 壳面气氛光（裁在表壳圆内）
    p.save()
    clip = QPainterPath()
    clip.addEllipse(QRectF(cx - 196.0, cy - 196.0, 392.0, 392.0))
    p.setClipPath(clip)
    aa = math.radians(sweep)
    gx, gy = cx + 191.0 * math.cos(aa), cy + 191.0 * math.sin(aa)
    g = QRadialGradient(gx, gy, 24.0)
    g.setColorAt(0.0, QColor(255, 248, 236, 72))
    g.setColorAt(1.0, QColor(255, 240, 220, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(g))
    p.drawEllipse(QRectF(gx - 24, gy - 24, 48, 48))
    p.restore()


def fx_year_ring(p, cx, cy, local, ctx):
    """r=170.4 细轨 + 玫瑰金填充（自春分顺时针累计太阳黄经）。
    该半径落在实测干净暗带内（sd≈8~11），罗马字墨迹与分钟刻度都碰不到。"""
    rect = QRectF(cx - YEAR_R, cy - YEAR_R, 2 * YEAR_R, 2 * YEAR_R)
    p.setPen(QPen(QColor(58, 66, 80, 210), 2.0))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(rect)
    deg = ctx['sun_lon'] % 360.0
    p.setPen(QPen(ac.MECH_ROSE, 2.0))
    p.drawArc(rect, 90 * 16, int(-deg * 16))
    for d in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(90.0 - d)
        p.setPen(QPen(QColor(126, 134, 148, 190), 1.0))
        p.drawLine(QLineF(cx + (YEAR_R - 2.6) * math.cos(a), cy - (YEAR_R - 2.6) * math.sin(a),
                          cx + (YEAR_R + 2.6) * math.cos(a), cy - (YEAR_R + 2.6) * math.sin(a)))
    for d, col, rr in ((0.0, QColor(146, 106, 68), 2.0), (deg, QColor(252, 214, 170), 2.8)):
        a = math.radians(90.0 - d)
        mx, my = cx + YEAR_R * math.cos(a), cy - YEAR_R * math.sin(a)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(col))
        p.drawEllipse(QRectF(mx - rr, my - rr, 2 * rr, 2 * rr))


S = 2000
K = S / ac.BASE


def render(fns, local=None):
    local = local or LOCAL
    ctx = ctx_of(local)
    pm = QPixmap(S, S)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    p.scale(K, K)
    w.paint_mechanical(p, ctx)
    for fn in fns:
        fn(p, 200.0, 200.0, local, ctx)
    p.end()
    return pm


def unwrap(im, a_center_deg, a_span_deg, r0, r1, out_w, out_h):
    """极坐标展开：x=角度(a_center±span/2)，y=半径(r1→r0 自上而下)。"""
    arr = np.asarray(im.convert('RGB'))
    xs = np.linspace(a_center_deg - a_span_deg / 2.0,
                     a_center_deg + a_span_deg / 2.0, out_w)
    ys = np.linspace(r1, r0, out_h)          # 顶部=外圈
    aa = np.radians(xs)
    rr = ys
    gx, gy = np.meshgrid(aa, rr)
    sx = (200.0 + gy * np.cos(gx)) * K
    sy = (200.0 + gy * np.sin(gx)) * K
    sx = np.clip(sx, 0, arr.shape[1] - 1).astype(np.int32)
    sy = np.clip(sy, 0, arr.shape[0] - 1).astype(np.int32)
    out = arr[sy, sx]
    return Image.fromarray(out)


sec_ang = LOCAL.second * 6.0 - 90.0
glint_ang = (LOCAL.timestamp() * 15.0) % 360.0
SUNSET_ANG = 90.0 - ((SUNSET - 12.0) / 24.0) * 360.0

EFFECTS = [
    ('① 秒点流光', fx_second_glow, sec_ang, 96.0, 166.0, 197.0,
     '分钟轨道 r173-180：当前秒点亮 + 向后 10 格渐隐光尾'),
    ('② 昼夜弧', fx_day_night, SUNSET_ANG, 200.0, 174.0, 192.0,
     '玫瑰金环 r181.4-185：昼亮金 %.1f~%.1f h，夜深蓝' % (SUNRISE, SUNSET)),
    ('③ 表壳光泽流转', fx_case_glint, glint_ang, 200.0, 180.0, 198.0,
     '滚花 r187-196：光带绕壳流动 15°/s'),
    ('④ 年度进度环', fx_year_ring, -20.0, 200.0, 160.0, 180.0,
     'r170.4 细轨 + 玫瑰金填充：太阳黄经已走 %.0f°' % (CTX['sun_lon'] % 360)),
]

render([]).save('_b.png')
for i, (name, fn, *_rest) in enumerate(EFFECTS):
    render([fn]).save('_e_%02d.png' % i)

ZW, ZH = 560, 190
CELL_W, CELL_H = 1080, 540
canvas = Image.new('RGB', (CELL_W * 2, CELL_H * 2), (23, 25, 29))
dr = ImageDraw.Draw(canvas)
try:
    fnt_t = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 27)
    fnt_s = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
except Exception:
    fnt_t = fnt_s = ImageFont.load_default()

for idx, (name, fn, za, zspan, r0, r1, note) in enumerate(EFFECTS):
    col, row = idx % 2, idx // 2
    ox, oy = col * CELL_W, row * CELL_H
    im = Image.open('_e_%02d.png' % idx)
    full = im.resize((480, 480), Image.LANCZOS)
    canvas.paste(full, (ox + 8, oy + 44), full)
    band = unwrap(im, za, zspan, r0, r1, ZW, ZH)
    canvas.paste(band, (ox + 496, oy + 52))
    dr.text((ox + 14, oy + 12), name, font=fnt_t, fill=(246, 246, 246))
    dr.text((ox + 496, oy + 30), '极坐标展开 · 上=外圈 r%.0f / 下=r%.0f' % (r1, r0),
            font=fnt_s, fill=(140, 146, 156))
    dr.text((ox + 14, oy + 498), note, font=fnt_s, fill=(168, 174, 184))
canvas.save('效果图_外圈动效.png')
print('saved 效果图_外圈动效.png')

render([fx_second_glow, fx_day_night, fx_case_glint, fx_year_ring]).save('_all.png')
Image.open('_all.png').resize((1020, 1020), Image.LANCZOS).save('效果图_外圈动效_组合.png')
print('saved 效果图_外圈动效_组合.png')
