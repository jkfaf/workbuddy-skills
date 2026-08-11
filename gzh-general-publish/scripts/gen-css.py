#!/usr/bin/env python3
"""
公众号 CSS 风格生成脚本（参数化）
根据主色调自动生成完整的公众号排版 CSS，包含 6 级字号层次、导语框、引用块、
高亮框、律师/作者卡片、版尾、表头等全部样式。

预设风格：
  lawyer-darkgold  深暗金奢华风（法律行业）  #6B4F0E
  business-blue    商务权威风（企业/商务）    #1A3A6B
  tech-purple      科技现代风（科技/互联网）  #6B2C91
  warm-orange      暖橙活力风（教育/生活）    #D4641E
  minimal-black    极简黑白风（通用/文艺）    #2C2C2C
  literature-green 文艺墨绿风（文化/传统）    #2D5016

用法:
  python3 gen-css.py --preset business-blue --output custom.css
  python3 gen-css.py --primary #1A3A6B --bg-light #F0F5FF --output custom.css
  python3 gen-css.py --list  # 列出所有预设
"""
import argparse
import sys

# ============ 预设配色方案 ============
PRESETS = {
    "lawyer-darkgold": {
        "name": "深暗金奢华风（法律行业）",
        "primary": "#6B4F0E",
        "primary_light": "#8B6914",
        "bg_light": "#F5EFE0",
        "bg_card": "#EDE3CC",
        "border_decor": "#C9B58A",
        "middle": "#A88840",
        "text_dark": "#3D2E08",
        "text_light": "#6B5520",
        "header_gradient": "linear-gradient(135deg, #F0F5FF 0%, #C8D8EE 25%, #6B8FBF 55%, #2C5286 80%, #1A3A6B 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#C9B58A",
    },
    "business-blue": {
        "name": "商务权威风（企业/商务）",
        "primary": "#1A3A6B",
        "primary_light": "#2C5286",
        "bg_light": "#F0F5FF",
        "bg_card": "#E0EAF7",
        "border_decor": "#9DB8D6",
        "middle": "#5A7FA8",
        "text_dark": "#1A2C4A",
        "text_light": "#3A5070",
        "header_gradient": "linear-gradient(135deg, #F0F5FF 0%, #C0D4EB 30%, #6B8FBF 60%, #2C5286 85%, #1A3A6B 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#C9B58A",
    },
    "tech-purple": {
        "name": "科技现代风（科技/互联网）",
        "primary": "#6B2C91",
        "primary_light": "#8B3FB0",
        "bg_light": "#F5F0FA",
        "bg_card": "#E8DCEF",
        "border_decor": "#B894C9",
        "middle": "#8B6BA8",
        "text_dark": "#2C1A3D",
        "text_light": "#4A3A5C",
        "header_gradient": "linear-gradient(135deg, #F5F0FA 0%, #D4C0E0 30%, #8B6BA8 60%, #6B2C91 85%, #4A1A6B 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#9DB8D6",
    },
    "warm-orange": {
        "name": "暖橙活力风（教育/生活）",
        "primary": "#D4641E",
        "primary_light": "#E8843A",
        "bg_light": "#FFF5EB",
        "bg_card": "#FFE8D1",
        "border_decor": "#F0B888",
        "middle": "#C08850",
        "text_dark": "#3D2A0E",
        "text_light": "#6B4A20",
        "header_gradient": "linear-gradient(135deg, #FFF5EB 0%, #FFE0C0 30%, #F0A868 60%, #D4641E 85%, #A04010 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#C9B58A",
    },
    "minimal-black": {
        "name": "极简黑白风（通用/文艺）",
        "primary": "#2C2C2C",
        "primary_light": "#4A4A4A",
        "bg_light": "#F8F8F8",
        "bg_card": "#EEEEEE",
        "border_decor": "#CCCCCC",
        "middle": "#888888",
        "text_dark": "#1A1A1A",
        "text_light": "#555555",
        "header_gradient": "linear-gradient(135deg, #F8F8F8 0%, #E0E0E0 30%, #888888 60%, #4A4A4A 85%, #2C2C2C 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#C9B58A",
    },
    "literature-green": {
        "name": "文艺墨绿风（文化/传统）",
        "primary": "#2D5016",
        "primary_light": "#4A7A2A",
        "bg_light": "#F0F5E8",
        "bg_card": "#DCE8C8",
        "border_decor": "#A8C088",
        "middle": "#6B8B4A",
        "text_dark": "#1A2C0E",
        "text_light": "#3A5020",
        "header_gradient": "linear-gradient(135deg, #F0F5E8 0%, #C8DCAF 30%, #6B8B4A 60%, #4A7A2A 85%, #2D5016 100%)",
        "header_text": "#FFFFFF",
        "header_accent": "#C9B58A",
    },
}

CSS_TEMPLATE = """/* ============================================
   公众号排版 CSS - {style_name}
   自动生成 by gen-css.py
   字号层次：
   - 主标题 22px / 章节标题 17px / 正文 16px
   - 设计元素 15px / 紧缩元素 14px / 明显紧缩 13px
   ============================================ */

/* ========== 全局字体 & 段落 ========== */
p {{
  font-family: "PingFang SC", "PingFangSC-light", -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "Hiragino Sans GB", "Microsoft YaHei UI", sans-serif;
  font-size: 16px;
  line-height: 1.8;
  letter-spacing: 1px;
  color: rgb(62, 62, 62);
  margin: 0 0 20px;
  text-align: justify;
}}

/* ========== h1 主标题 ========== */
h1 {{
  font-family: "PingFang SC", -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
  font-size: 22px;
  font-weight: bold;
  color: #2C2C2C;
  text-align: center;
  margin: 0 0 28px;
  letter-spacing: 1px;
  line-height: 1.5;
}}

/* ========== h2 章节标题 ========== */
h2 {{
  font-family: "PingFang SC", -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
  font-size: 17px;
  font-weight: bold;
  color: {primary};
  margin: 24px 0 14px;
  letter-spacing: 1px;
  line-height: 1.5;
}}

/* ========== 导语框 ========== */
.lead-box {{
  background: {bg_light};
  border-left: 4px solid {primary};
  border-radius: 0 6px 6px 0;
  padding: 18px 22px;
  margin: 20px 0 24px;
}}
.lead-label {{
  display: inline-block;
  background: {primary};
  color: #FFFFFF;
  font-size: 14px;
  font-weight: bold;
  padding: 3px 12px;
  border-radius: 3px;
  margin-bottom: 10px;
  letter-spacing: 1px;
}}
.lead-content {{
  font-size: 15px;
  color: {text_dark};
  line-height: 1.8;
  margin: 0;
}}

/* ========== 引用块 ========== */
.quote-box {{
  background: {bg_card};
  border: 1px dashed {border_decor};
  border-radius: 6px;
  padding: 18px 22px;
  margin: 20px 0;
  position: relative;
}}
.quote-mark {{
  font-size: 32px;
  color: {middle};
  font-family: Georgia, serif;
  line-height: 1;
  margin-bottom: 8px;
}}
.quote-text {{
  font-size: 15px;
  color: {text_dark};
  line-height: 1.8;
  margin: 0 0 8px;
  font-style: italic;
}}
.quote-sub {{
  font-size: 14px;
  color: {text_light};
  margin: 0;
}}

/* ========== 高亮框 ========== */
.highlight-box {{
  background: {bg_light};
  border: 1px dashed {primary};
  border-radius: 6px;
  padding: 16px 20px;
  margin: 16px 0;
}}
.highlight-box p {{
  font-size: 15px;
  color: {text_dark};
  margin: 0;
}}

/* ========== 章节序号装饰 ========== */
.section-title {{
  margin: 28px 0 18px;
  padding: 0;
  border: none;
}}
.section-num {{
  display: inline-block;
  font-size: 28px;
  color: {middle};
  font-family: Georgia, serif;
  font-weight: bold;
  vertical-align: middle;
  margin-right: 8px;
}}
.section-text {{
  display: inline-block;
  font-size: 17px;
  color: {primary};
  font-weight: bold;
  vertical-align: middle;
}}

/* ========== 图片样式 ========== */
figure {{
  width: 90%;
  margin: 20px auto;
  text-align: center;
}}
figure img {{
  width: 100%;
  border-radius: 6px;
}}
figcaption {{
  text-align: center;
  color: #999;
  font-size: 13px;
  margin-top: 10px;
}}

/* ========== 分隔线 ========== */
hr {{
  border: none;
  height: 1px;
  background: {border_decor};
  margin: 30px 0;
}}

/* ========== 作者/人物卡片 ========== */
.lawyer-card {{
  background: {bg_light};
  border: 1px solid {border_decor};
  border-radius: 8px;
  padding: 20px;
  margin: 24px 0;
}}
.lawyer-avatar {{
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid {primary};
  box-shadow: 0 0 0 3px rgba({primary_rgb}, 0.3);
  display: inline-block;
  vertical-align: middle;
  margin-right: 16px;
}}
.lawyer-info {{
  display: inline-block;
  vertical-align: middle;
}}
.lawyer-name {{
  font-size: 14px;
  font-weight: bold;
  color: {text_dark};
  margin: 0 0 4px;
}}
.lawyer-title {{
  font-size: 13px;
  color: {text_light};
  margin: 0 0 6px;
}}
.lawyer-bio {{
  font-size: 13px;
  color: {text_light};
  line-height: 1.6;
  margin: 0;
}}

/* ========== 版尾卡片 ========== */
.gzh-footer {{
  background: #2C2C2C;
  border-radius: 8px;
  padding: 24px 20px;
  margin: 30px 0 0;
  text-align: center;
}}
.gzh-footer-name {{
  font-size: 13px;
  color: #FFFFFF;
  font-weight: bold;
  letter-spacing: 2px;
  margin: 0 0 8px;
}}
.gzh-footer-slogan {{
  font-size: 13px;
  color: #AAAAAA;
  margin: 0 0 16px;
}}
.gzh-footer-qrcode {{
  width: 120px;
  height: 120px;
  border-radius: 6px;
  border: 2px solid {primary};
  margin: 0 auto 8px;
}}
.gzh-footer-tip {{
  font-size: 13px;
  color: #888888;
  margin: 0;
}}
"""


def hex_to_rgb(hex_color):
    """#6B4F0E -> 107,79,14"""
    hex_color = hex_color.lstrip("#")
    return f"{int(hex_color[0:2], 16)},{int(hex_color[2:4], 16)},{int(hex_color[4:6], 16)}"


def generate_css(config):
    """根据配色配置生成完整 CSS"""
    primary_rgb = hex_to_rgb(config["primary"])
    return CSS_TEMPLATE.format(
        style_name=config["name"],
        primary=config["primary"],
        primary_light=config["primary_light"],
        bg_light=config["bg_light"],
        bg_card=config["bg_card"],
        border_decor=config["border_decor"],
        middle=config["middle"],
        text_dark=config["text_dark"],
        text_light=config["text_light"],
        primary_rgb=primary_rgb,
    )


def main():
    parser = argparse.ArgumentParser(description="公众号 CSS 风格生成脚本")
    parser.add_argument("--preset", type=str, help="预设风格名称")
    parser.add_argument("--primary", type=str, help="自定义主色（如 #1A3A6B）")
    parser.add_argument("--bg-light", type=str, help="自定义浅背景色")
    parser.add_argument("--output", "-o", type=str, default="custom.css", help="输出文件路径")
    parser.add_argument("--list", action="store_true", help="列出所有预设风格")
    args = parser.parse_args()

    if args.list:
        print("可用预设风格：")
        for key, config in PRESETS.items():
            print(f"  {key:20s}  {config['name']}  主色: {config['primary']}")
        return

    if args.preset:
        if args.preset not in PRESETS:
            print(f"错误：预设 '{args.preset}' 不存在，用 --list 查看可用预设", file=sys.stderr)
            sys.exit(1)
        config = PRESETS[args.preset].copy()
    elif args.primary:
        # 自定义配色：根据主色自动推导其他色
        config = {
            "name": f"自定义风格（主色 {args.primary}）",
            "primary": args.primary,
            "primary_light": args.primary,
            "bg_light": args.bg_light or "#F5F5F5",
            "bg_card": "#EEEEEE",
            "border_decor": "#CCCCCC",
            "middle": "#888888",
            "text_dark": "#2C2C2C",
            "text_light": "#555555",
        }
    else:
        parser.print_help()
        sys.exit(1)

    css = generate_css(config)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"✓ CSS 已生成: {args.output}")
    print(f"  风格: {config['name']}")
    print(f"  主色: {config['primary']}")


if __name__ == "__main__":
    main()
