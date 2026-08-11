#!/usr/bin/env python3
"""
公众号封面图生成脚本（参数化模板）
支持两种布局：
  tianzi: 2x2 田字格四字布局（适合微信 1:1 正方形裁剪）
  title:  双行标题 + 副标题（横版 2.35:1）

用法:
  python3 gen-cover.py --bg <背景图> --output <输出.png> --layout tianzi --text "诚明动态" --logo <logo.png>
  python3 gen-cover.py --bg <背景图> --output <输出.png> --layout title --text "建设工程|法律风险防控" --subtitle "杨国胜律师·专题培训" --logo <logo.png>
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse
import os

FONT_HEI = '/System/Library/Fonts/STHeiti Medium.ttc'
FONT_HEI_LIGHT = '/System/Library/Fonts/STHeiti Light.ttc'

CANVAS_W, CANVAS_H = 900, 383  # 公众号推荐 2.35:1


def load_bg(bg_path):
    """加载背景图，裁剪缩放到 900x383"""
    bg = Image.open(bg_path).convert('RGB')
    bg_w, bg_h = bg.size
    target_ratio = CANVAS_W / CANVAS_H
    bg_ratio = bg_w / bg_h
    if bg_ratio > target_ratio:
        new_w = int(bg_h * target_ratio)
        left = (bg_w - new_w) // 2
        bg = bg.crop((left, 0, left + new_w, bg_h))
    else:
        new_h = int(bg_w / target_ratio)
        top = (bg_h - new_h) // 2
        bg = bg.crop((0, top, bg_w, top + new_h))
    return bg.resize((CANVAS_W, CANVAS_H), Image.LANCZOS).convert('RGBA')


def draw_centered_text(draw, text, y, font, fill, canvas_w=CANVAS_W):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (canvas_w - w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def layout_tianzi(bg_rgba, text, logo_path=None):
    """2x2 田字格四字布局（适合 1:1 正方形裁剪）"""
    draw = ImageDraw.Draw(bg_rgba)
    font_big = ImageFont.truetype(FONT_HEI, 92)
    chars = list(text[:4])  # 取前4字

    bbox = draw.textbbox((0, 0), chars[0], font=font_big)
    char_w = bbox[2] - bbox[0]
    char_h = bbox[3] - bbox[1]
    char_y_offset = bbox[1]

    gap_x, gap_y = 36, 12
    total_w = char_w * 2 + gap_x
    total_h = char_h * 2 + gap_y
    start_x = (CANVAS_W - total_w) // 2
    start_y = (CANVAS_H - total_h) // 2 - char_y_offset

    positions = [
        (start_x, start_y),
        (start_x + char_w + gap_x, start_y),
        (start_x, start_y + char_h + gap_y),
        (start_x + char_w + gap_x, start_y + char_h + gap_y),
    ]
    # 先画阴影层
    for char, (x, y) in zip(chars, positions):
        draw.text((x + 2, y + 2), char, font=font_big, fill=(0, 0, 0, 120))
    # 再画白色主字
    for char, (x, y) in zip(chars, positions):
        draw.text((x, y), char, font=font_big, fill=(255, 255, 255))

    # 右下角小 logo
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        logo_h = 22
        logo_ratio = logo.size[0] / logo.size[1]
        logo_w = int(logo_h * logo_ratio)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        bg_rgba.paste(logo, (CANVAS_W - logo_w - 28, CANVAS_H - logo_h - 18), logo)
    return bg_rgba


def layout_title(bg_rgba, text, subtitle, logo_path=None):
    """双行标题 + 副标题布局"""
    draw = ImageDraw.Draw(bg_rgba)
    parts = text.split('|') if '|' in text else [text]
    font_title1 = ImageFont.truetype(FONT_HEI, 56)
    font_title2 = ImageFont.truetype(FONT_HEI, 72)
    font_sub = ImageFont.truetype(FONT_HEI, 28)

    title_y = 95
    if len(parts) >= 1:
        h1 = draw_centered_text(draw, parts[0], title_y, font_title1, (255, 255, 255))
    if len(parts) >= 2:
        draw_centered_text(draw, parts[1], title_y + h1 + 8, font_title2, (255, 255, 255))
    if subtitle:
        sub_y = title_y + (h1 + 8) * 2 + 16
        draw_centered_text(draw, subtitle, sub_y, font_sub, (201, 181, 138))

    # 右下角小 logo
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        logo_h = 22
        logo_ratio = logo.size[0] / logo.size[1]
        logo_w = int(logo_h * logo_ratio)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        bg_rgba.paste(logo, (CANVAS_W - logo_w - 28, CANVAS_H - logo_h - 18), logo)
    return bg_rgba


def main():
    parser = argparse.ArgumentParser(description='生成公众号封面图')
    parser.add_argument('--bg', required=True, help='背景图路径')
    parser.add_argument('--output', required=True, help='输出 PNG 路径')
    parser.add_argument('--layout', choices=['tianzi', 'title'], default='tianzi', help='布局：tianzi(田字格) 或 title(标题)')
    parser.add_argument('--text', required=True, help='田字格: 四字文本; 标题: 用|分隔两行')
    parser.add_argument('--subtitle', help='副标题（仅 title 布局）')
    parser.add_argument('--logo', help='右下角 logo PNG 路径')
    args = parser.parse_args()

    bg_rgba = load_bg(args.bg)

    if args.layout == 'tianzi':
        bg_rgba = layout_tianzi(bg_rgba, args.text, args.logo)
    else:
        bg_rgba = layout_title(bg_rgba, args.text, args.subtitle, args.logo)

    # 保存（保留 RGBA 透明通道，不要 convert('RGB')）
    bg_rgba.save(args.output, 'PNG', optimize=True)
    print(f'✓ 封面已生成: {args.output}')
    print(f'  尺寸: {bg_rgba.size}')
    print(f'  大小: {os.path.getsize(args.output)/1024:.1f} KB')


if __name__ == '__main__':
    main()
