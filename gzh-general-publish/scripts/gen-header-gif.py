#!/usr/bin/env python3
"""
公众号文章表头动图 GIF 生成脚本（参数化模板）
深邃蓝渐变背景 + 静态 logo + 文字淡入淡出 + 柔和金色扫光

用法:
  python3 gen-header-gif.py --logo <logo.png> --output header.gif \
    --firm "湖 北 诚 明 律 师 事 务 所" --en "HUBEI CHENGMING LAW FIRM" \
    --slogan "专 业 · 诚 信 · 高 效"
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os
import argparse

FONT_HEI = '/System/Library/Fonts/STHeiti Medium.ttc'
FONT_HEI_LIGHT = '/System/Library/Fonts/STHeiti Light.ttc'

# 深邃蓝渐变站点（顶浅底深）
GRADIENT_STOPS = [
    (0.00, (240, 245, 255)),  # #F0F5FF
    (0.25, (200, 216, 238)),  # #C8D8EE
    (0.55, (107, 143, 191)),  # #6B8FBF
    (0.80, (44, 82, 134)),    # #2C5286
    (1.00, (26, 58, 107)),    # #1A3A6B
]

GOLD = (201, 181, 138)       # 金色 #C9B58A
DEEP_BLUE = (26, 58, 107)    # 深蓝 #1A3A6B


def make_gradient_bg(w, h):
    bg = Image.new('RGB', (w, h))
    px = bg.load()
    for y in range(h):
        ratio = y / (h - 1)
        for i in range(len(GRADIENT_STOPS) - 1):
            r0, c0 = GRADIENT_STOPS[i]
            r1, c1 = GRADIENT_STOPS[i + 1]
            if r0 <= ratio <= r1:
                t = (ratio - r0) / (r1 - r0)
                r = int(c0[0] + (c1[0] - c0[0]) * t)
                g = int(c0[1] + (c1[1] - c0[1]) * t)
                b = int(c0[2] + (c1[2] - c0[2]) * t)
                for x in range(w):
                    px[x, y] = (r, g, b)
                break
    return bg


def draw_static_layer(img, scale, logo_path=None):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    # 外边框
    draw.rectangle([0, 0, w - 1, h - 1], outline=DEEP_BLUE, width=3 * scale)
    # 顶部金色光带
    bar_y = 12 * scale
    bar_w = 200 * scale
    bar_x = (w - bar_w) // 2
    for i in range(3 * scale):
        alpha_ratio = 1 - abs(i - 1.5 * scale) / (1.5 * scale)
        c = tuple(int(GOLD[j] * alpha_ratio * 0.5) for j in range(3))
        draw.line([(bar_x, bar_y + i), (bar_x + bar_w, bar_y + i)], fill=c, width=1)
    # Logo（静态）
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        logo_h = 40 * scale
        logo_ratio = logo.size[0] / logo.size[1]
        logo_w = int(logo_h * logo_ratio)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        logo = logo.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        logo_x = (w - logo_w) // 2
        logo_y = 22 * scale
        img.paste(logo, (logo_x, logo_y), logo)
    return img


def draw_text_layer(w, h, scale, alpha, firm, en, slogan):
    """绘制文字层，alpha 控制整体透明度（0-255），用 sin(πt) 实现淡入淡出"""
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if alpha <= 0:
        return layer
    draw = ImageDraw.Draw(layer)

    # 律所中文名
    font_firm = ImageFont.truetype(FONT_HEI, 17 * scale)
    bbox = draw.textbbox((0, 0), firm, font=font_firm)
    fw = bbox[2] - bbox[0]
    draw.text(((w - fw) // 2, 72 * scale), firm, font=font_firm, fill=(255, 255, 255, alpha))

    # 英文名
    en_alpha = int(alpha * 0.85)
    font_en = ImageFont.truetype(FONT_HEI_LIGHT, 10 * scale)
    bbox = draw.textbbox((0, 0), en, font=font_en)
    ew = bbox[2] - bbox[0]
    draw.text(((w - ew) // 2, 98 * scale), en, font=font_en, fill=(220, 230, 245, en_alpha))

    # 金色分隔线
    div_w = 40 * scale
    div_x = (w - div_w) // 2
    div_y = 120 * scale
    draw.rectangle([div_x, div_y, div_x + div_w, div_y + scale], fill=(*GOLD, alpha))

    # 副标语
    font_slogan = ImageFont.truetype(FONT_HEI, 13 * scale)
    bbox = draw.textbbox((0, 0), slogan, font=font_slogan)
    sw = bbox[2] - bbox[0]
    draw.text(((w - sw) // 2, 130 * scale), slogan, font=font_slogan, fill=(*GOLD, alpha))
    return layer


def make_sweep_light(w, h, scale, x_offset, intensity=1.0):
    """柔和斜向金色扫光，intensity 控制亮度"""
    if intensity <= 0:
        return Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sweep = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sweep)
    band_w = 180 * scale
    angle = -12
    max_alpha = int(55 * intensity)
    rad = math.radians(angle)
    tan_a = math.tan(rad)
    for i in range(-band_w // 2, band_w // 2):
        dist = abs(i)
        if dist > band_w // 2:
            continue
        alpha = int(max_alpha * math.exp(-(dist / (band_w // 4)) ** 2))
        if alpha <= 0:
            continue
        color = (*GOLD, alpha)
        line_x_offset = x_offset + i
        x_top = line_x_offset
        x_bot = line_x_offset + h * tan_a
        draw.line([(x_top, 0), (x_bot, h)], fill=color, width=1 * scale)
    return sweep.filter(ImageFilter.GaussianBlur(radius=4 * scale))


def main():
    parser = argparse.ArgumentParser(description='生成公众号表头动图 GIF')
    parser.add_argument('--logo', required=True, help='Logo PNG 路径')
    parser.add_argument('--output', required=True, help='输出 GIF 路径')
    parser.add_argument('--firm', default='湖 北 诚 明 律 师 事 务 所', help='律所中文名')
    parser.add_argument('--en', default='HUBEI CHENGMING LAW FIRM', help='英文名')
    parser.add_argument('--slogan', default='专 业 · 诚 信 · 高 效', help='副标语')
    parser.add_argument('--frames', type=int, default=36, help='帧数')
    parser.add_argument('--duration', type=int, default=70, help='每帧时长(ms)')
    args = parser.parse_args()

    scale = 2  # 2x 渲染再缩小提升清晰度
    w, h = 640 * scale, 170 * scale

    print('生成静态背景层...')
    bg = make_gradient_bg(w, h)
    bg = draw_static_layer(bg, scale, args.logo)
    bg_rgba = bg.convert('RGBA')

    n = args.frames
    print(f'生成 {n} 帧（文字淡入淡出 + 扫光）...')
    frames = []
    for i in range(n):
        t = i / n
        text_alpha = int(255 * math.sin(math.pi * t))
        text_alpha = max(0, min(255, text_alpha))
        frame = bg_rgba.copy()
        # 文字层
        frame = Image.alpha_composite(frame, draw_text_layer(w, h, scale, text_alpha, args.firm, args.en, args.slogan))
        # 扫光（只在文字可见时出现）
        if text_alpha > 60:
            sweep_intensity = (text_alpha - 60) / 195
            sweep_t = max(0, min(1, (t - 0.2) / 0.6))
            x_off = -200 * scale + int(sweep_t * (w + 400 * scale))
            frame = Image.alpha_composite(frame, make_sweep_light(w, h, scale, x_off, sweep_intensity))
        # 缩小到 1x
        frame_small = frame.resize((640, 170), Image.LANCZOS)
        frame_p = frame_small.convert('RGB').quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
        frames.append(frame_p)

    print('保存 GIF...')
    frames[0].save(
        args.output, save_all=True, append_images=frames[1:],
        duration=args.duration, loop=0, disposal=2, optimize=True
    )
    print(f'✓ 表头动图已生成: {args.output}')
    print(f'  尺寸: 640×170  帧数: {n}  大小: {os.path.getsize(args.output)/1024:.1f} KB')


if __name__ == '__main__':
    main()
