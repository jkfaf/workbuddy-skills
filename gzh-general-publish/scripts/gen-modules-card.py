#!/usr/bin/env python3
"""
五大模块卡片图生成器
生成 2×2+1 布局的卡片图，替代微信不兼容的 <table> 布局。
微信编辑器对 <img> 标签最友好，不会做任何标签转换。

设计：圆形徽章（序号）+ 名称文字并排，整体居中。
序号用图形化徽章区分于名称文字，字体与正文相当。
"""

from PIL import Image, ImageDraw, ImageFont
import sys

# ============ 配置 ============
W, H = 600, 260        # 宽度不变，高度从 320 缩到 260（字体小了）
MARGIN = 10            # 外边距
GAP = 8                # 卡片间距
RADIUS = 8             # 卡片圆角
BADGE_D = 28           # 圆形徽章直径
GAP_BADGE_NAME = 10    # 徽章与名称的水平间距

# 颜色（与文章深暗金色调一致）
BG_COLOR = '#F5EFE0'       # 卡片背景
BORDER_COLOR = '#C9B58A'   # 卡片边框
BADGE_BG = '#6B4F0E'       # 徽章背景（暗金）
BADGE_TEXT = '#FFFFFF'     # 徽章数字（白色）
NAME_COLOR = '#3D2E08'     # 名称颜色（深棕）
CANVAS_BG = '#FFFFFF'      # 画布背景

# 字体
FONT_NUM = '/System/Library/Fonts/STHeiti Medium.ttc'
FONT_NAME = '/System/Library/Fonts/Hiragino Sans GB.ttc'
NUM_SIZE = 13              # 徽章数字字号（小，在圆形里）
NAME_SIZE = 18             # 名称字号（与正文 16px 相当）

# 五大模块内容（可通过命令行参数覆盖）
DEFAULT_MODULES = [
    ('01', '招投标合规'),
    ('02', '合同效力认定'),
    ('03', '施工过程管理'),
    ('04', '竣工验收与结算'),
    ('05', '建筑材料采购'),
]


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_card(draw, x, y, w, h, num, name, font_num, font_name):
    """绘制单个圆角卡片：圆形徽章 + 名称并排，整体居中"""
    # 圆角矩形背景
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=RADIUS,
        fill=BG_COLOR,
        outline=BORDER_COLOR,
        width=1
    )

    # 测量名称尺寸
    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    name_h = name_bbox[3] - name_bbox[1]

    # 整体宽度 = 徽章 + 间距 + 名称
    total_w = BADGE_D + GAP_BADGE_NAME + name_w

    # 整体水平居中
    start_x = x + (w - total_w) // 2
    badge_x = start_x
    badge_y = y + (h - BADGE_D) // 2

    # 画圆形徽章（暗金底）
    draw.ellipse(
        [badge_x, badge_y, badge_x + BADGE_D, badge_y + BADGE_D],
        fill=BADGE_BG
    )

    # 徽章数字（白色，居中在圆内）
    num_bbox = draw.textbbox((0, 0), num, font=font_num)
    num_w = num_bbox[2] - num_bbox[0]
    num_h = num_bbox[3] - num_bbox[1]
    num_x = badge_x + (BADGE_D - num_w) // 2 - num_bbox[0]
    num_y = badge_y + (BADGE_D - num_h) // 2 - num_bbox[1]
    draw.text((num_x, num_y), num, fill=BADGE_TEXT, font=font_num)

    # 名称文字（徽章右侧，垂直居中）
    name_x = start_x + BADGE_D + GAP_BADGE_NAME
    name_y = y + (h - name_h) // 2 - name_bbox[1]
    draw.text((name_x, name_y), name, fill=NAME_COLOR, font=font_name)


def main():
    # 支持命令行传入模块内容：python3 gen-modules-card.py "01|模块一" "02|模块二" ...
    if len(sys.argv) > 1:
        modules = []
        for arg in sys.argv[1:]:
            parts = arg.split('|', 1)
            if len(parts) == 2:
                modules.append((parts[0], parts[1]))
        if len(modules) < 5:
            print('⚠️  传入的模块不足 5 个，使用默认值补全')
            while len(modules) < 5:
                modules.append(DEFAULT_MODULES[len(modules)])
        modules = modules[:5]
    else:
        modules = DEFAULT_MODULES

    # 创建画布
    img = Image.new('RGB', (W, H), CANVAS_BG)
    draw = ImageDraw.Draw(img)

    # 加载字体
    font_num = load_font(FONT_NUM, NUM_SIZE)
    font_name = load_font(FONT_NAME, NAME_SIZE)

    # 计算卡片尺寸
    card_w = (W - MARGIN * 2 - GAP) // 2       # 两列
    card_h = (H - MARGIN * 2 - GAP * 2) // 3   # 三行

    # 第 1 行（2 个卡片）
    draw_card(draw, MARGIN, MARGIN, card_w, card_h,
              modules[0][0], modules[0][1], font_num, font_name)
    draw_card(draw, MARGIN + card_w + GAP, MARGIN, card_w, card_h,
              modules[1][0], modules[1][1], font_num, font_name)

    # 第 2 行（2 个卡片）
    y2 = MARGIN + card_h + GAP
    draw_card(draw, MARGIN, y2, card_w, card_h,
              modules[2][0], modules[2][1], font_num, font_name)
    draw_card(draw, MARGIN + card_w + GAP, y2, card_w, card_h,
              modules[3][0], modules[3][1], font_num, font_name)

    # 第 3 行（1 个卡片，占满整行）
    y3 = y2 + card_h + GAP
    draw_card(draw, MARGIN, y3, W - MARGIN * 2, card_h,
              modules[4][0], modules[4][1], font_num, font_name)

    # 保存
    output = 'modules-card.png'
    img.save(output, 'PNG', optimize=True)
    print(f'✓ 五大模块卡片图已生成: {output} ({W}×{H})')

    # 输出 base64（供 inline-css.js 使用）
    import base64
    with open(output, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    print(f'✓ base64 长度: {len(b64)} 字符')


if __name__ == '__main__':
    main()
