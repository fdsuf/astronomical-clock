# -*- coding: utf-8 -*-
"""生成 exe 程序图标 app.ico：多尺寸分别绘制（小尺寸简化笔画，避免糊成一团）。

用法：python tools/make_icon.py
输出：app.ico（同时留下各尺寸 PNG 便于检查）
"""
import math
import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import (QPixmap, QPainter, QColor, QPen, QBrush, QRadialGradient,
                         QConicalGradient, QPolygonF)
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
from PIL import Image

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 机械表配色（与主程序 MECH_* 一致）
BG_IN = "#2c3139"
BG_OUT = "#12141a"
ROSE_L = "#f0c79a"
ROSE_D = "#8a5b35"
STEEL = "#cfd8e2"


def draw(size):
    """按目标像素尺寸绘制图标。size>=48 用 4x 超采样后缩小，小尺寸直接按整数画。

    分级策略（16px 下塞满 60 格刻度必糊，必须按尺寸裁减信息量）：
      >=48px  60 格刻度（5 格加长）+ 内圈细线 + 中心轴双环
      >=32px  12 格整点刻度
      >=24px  4 个主刻度（12/3/6/9），细一些
      <24px   不画刻度——16px 下任何刻度都会糊成十字/噪点，
              只留「深色圆盘 + 金色外圈 + 两根粗指针」，反而最像表盘
    """
    ss = 4 if size <= 64 else 2
    px = size * ss
    pm = QPixmap(px, px)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.scale(ss, ss)

    c = size / 2.0
    detail = size >= 48
    mid = 32 <= size < 48
    small = 24 <= size < 32
    tiny = size < 24
    r = c - size * 0.045         # 留一点边距

    # 盘面：径向渐变（中心略亮）
    g = QRadialGradient(c, c * 0.78, r * 1.35)
    g.setColorAt(0.0, QColor(BG_IN))
    g.setColorAt(1.0, QColor(BG_OUT))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(g))
    p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))

    # 外圈玫瑰金（锥形渐变模拟金属反光）；小尺寸加粗以保证轮廓可辨
    rw = max(1.2, size * (0.085 if tiny else (0.07 if small else 0.055)))
    cg = QConicalGradient(c, c, 55)
    for pos, col in [(0.0, "#f2caa2"), (0.28, "#8a5b35"),
                     (0.55, "#e3b083"), (0.8, "#6e4325"), (1.0, "#f2caa2")]:
        cg.setColorAt(pos, QColor(col))
    p.setPen(QPen(QBrush(cg), rw))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))

    # 内圈细线（仅大尺寸）
    if detail:
        p.setPen(QPen(QColor(ROSE_D), max(0.6, size * 0.008)))
        ri = r - rw * 1.4
        p.drawEllipse(QRectF(c - ri, c - ri, 2 * ri, 2 * ri))

    # 刻度：按尺寸分档，极小尺寸完全不要刻度
    if detail:
        for k in range(60):
            a = math.radians(k * 6.0 - 90.0)
            major = (k % 5 == 0)
            r1 = r - rw * 1.6 - size * (0.085 if major else 0.045)
            r2 = r - rw * 1.6 - size * 0.012
            pen = QPen(QColor(STEEL), max(0.9, size * (0.016 if major else 0.007)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(c + r1 * math.cos(a), c + r1 * math.sin(a),
                              c + r2 * math.cos(a), c + r2 * math.sin(a)))
    elif mid:
        for k in range(12):
            a = math.radians(k * 30.0 - 90.0)
            if k % 3 != 0:
                continue          # 32px 下次刻度会渲染成灰色小块，只保留 4 个整点
            r1 = r - rw * 1.6 - size * 0.12
            r2 = r - rw * 1.6 - size * 0.03
            pen = QPen(QColor("#dcc8ab"), max(1.0, size * 0.038))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(c + r1 * math.cos(a), c + r1 * math.sin(a),
                              c + r2 * math.cos(a), c + r2 * math.sin(a)))
    elif small:
        for k in range(4):
            a = math.radians(k * 90.0 - 90.0)
            r1 = r - rw * 1.5 - size * 0.14
            r2 = r - rw * 1.5 - size * 0.07
            pen = QPen(QColor("#d8c3a5"), max(1.0, size * 0.035))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QLineF(c + r1 * math.cos(a), c + r1 * math.sin(a),
                              c + r2 * math.cos(a), c + r2 * math.sin(a)))
    # tiny：刻意不画刻度

    # 指针：经典 10:10 姿态（视觉平衡最好看的表盘摆法）
    hour_a = math.radians((10 + 10 / 60.0) * 30.0 - 90.0)
    min_a = math.radians(10 * 6.0 - 90.0)
    # 极小尺寸没有刻度可依靠，指针是唯一辨识元素，故画得更长更粗
    hand_len = r - rw * 1.2 - size * (0.03 if tiny else 0.06)

    def hand(angle, length, width, color):
        pen = QPen(QColor(color), width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QLineF(c, c, c + length * math.cos(angle),
                          c + length * math.sin(angle)))

    if tiny:
        hand(min_a, hand_len * 0.92, max(2.0, size * 0.115), "#ffe8cc")  # 分针
        hand(hour_a, hand_len * 0.55, max(2.2, size * 0.135), "#ffd9a8")  # 时针
    else:
        hand(min_a, hand_len * 0.95, max(1.4, size * 0.052), ROSE_L)
        hand(hour_a, hand_len * 0.62, max(2.0, size * 0.072), "#f7dcb8")

    # 中心轴：玫瑰金圆点 + 深色芯
    cr = max(1.2, size * (0.075 if tiny else 0.05))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(ROSE_L)))
    p.drawEllipse(QRectF(c - cr, c - cr, 2 * cr, 2 * cr))
    if detail:
        p.setBrush(QBrush(QColor(BG_OUT)))
        cr2 = cr * 0.42
        p.drawEllipse(QRectF(c - cr2, c - cr2, 2 * cr2, 2 * cr2))
    p.end()
    return pm.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)


def main():
    app = QApplication(sys.argv)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = []
    for s in sizes:
        pm = draw(s)
        fn = os.path.join(APP_DIR, "_icon_%d.png" % s)
        pm.save(fn)
        imgs.append(Image.open(fn).convert("RGBA"))
        print("  绘制 %3dpx" % s)

    ico = os.path.join(APP_DIR, "app.ico")
    base = imgs[-1]                      # 256px 作为主体
    base.save(ico, format="ICO",
              sizes=[(s, s) for s in sizes],
              append_images=imgs[:-1])   # 各尺寸用专门绘制的那一张，而非缩放
    print("已生成 %s (%.1f KB)" % (ico, os.path.getsize(ico) / 1024.0))

    # 预览拼图（浅底），确认小尺寸不糊
    from PIL import ImageDraw
    pad, big = 12, 96
    W = pad + sum(max(s, big // 2) + pad for s in sizes)
    canvas = Image.new("RGB", (W, big + pad * 2 + 16), (246, 246, 246))
    dr = ImageDraw.Draw(canvas)
    x = pad
    for s, im in zip(sizes, imgs):
        show = im if s >= big else im.resize((big, big), Image.NEAREST)
        canvas.paste(show, (x, pad), show)
        dr.text((x, pad + big + 2), str(s), fill=(40, 40, 40))
        x += max(s, big // 2) + pad
    canvas.save(os.path.join(APP_DIR, "_icon_preview.png"))
    print("已生成预览 _icon_preview.png")


if __name__ == "__main__":
    main()
