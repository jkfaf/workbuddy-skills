#!/usr/bin/env python3
"""
render_gzh.py - Markdown 到微信公众号 HTML 的渲染脚本

将 Markdown 文件转换为带有主题样式的 HTML，可直接复制粘贴到微信公众号编辑器。

用法:
    python3 render_gzh.py --input article.md --theme default --output article.html
    python3 render_gzh.py -i article.md -t fresh-blue -o article.html
    python3 render_gzh.py -i article.md -t default --code-theme monokai -o out.html
    python3 render_gzh.py -i article.md -t default --custom-css my-style.css -o out.html
"""

import argparse
import html
import re
import os
import sys
from pathlib import Path

# ============================================================
# 主题样式定义
# ============================================================

THEMES = {
    "default": {
        "primary": "#07c160",
        "accent": "#07c160",
        "text": "#3f3f3f",
        "text_secondary": "#888888",
        "bg": "#ffffff",
        "border": "#e8e8e8",
        "code_bg": "#f6f8fa",
        "code_text": "#c7254e",
        "quote_bg": "#f7f7f7",
        "quote_border": "#07c160",
    },
    "elegant-black": {
        "primary": "#2d2d2d",
        "accent": "#c0392b",
        "text": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "bg": "#fafafa",
        "border": "#d0d0d0",
        "code_bg": "#2d2d2d",
        "code_text": "#e74c3c",
        "quote_bg": "#f0f0f0",
        "quote_border": "#c0392b",
    },
    "fresh-blue": {
        "primary": "#3498db",
        "accent": "#2980b9",
        "text": "#2c3e50",
        "text_secondary": "#95a5a6",
        "bg": "#ffffff",
        "border": "#bee5eb",
        "code_bg": "#eaf2f8",
        "code_text": "#2980b9",
        "quote_bg": "#eaf2f8",
        "quote_border": "#3498db",
    },
    "warm-orange": {
        "primary": "#e67e22",
        "accent": "#d35400",
        "text": "#34495e",
        "text_secondary": "#95a5a6",
        "bg": "#fffaf5",
        "border": "#fdebd0",
        "code_bg": "#fef5e7",
        "code_text": "#d35400",
        "quote_bg": "#fef5e7",
        "quote_border": "#e67e22",
    },
    "geek-green": {
        "primary": "#27ae60",
        "accent": "#2ecc71",
        "text": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "bg": "#f8f9fa",
        "border": "#d4efdf",
        "code_bg": "#282c34",
        "code_text": "#abb2bf",
        "quote_bg": "#eafaf1",
        "quote_border": "#27ae60",
    },
    "rose-red": {
        "primary": "#e74c3c",
        "accent": "#c0392b",
        "text": "#2c3e50",
        "text_secondary": "#95a5a6",
        "bg": "#fff5f5",
        "border": "#fadbd8",
        "code_bg": "#fdedec",
        "code_text": "#c0392b",
        "quote_bg": "#fdedec",
        "quote_border": "#e74c3c",
    },
}


def generate_css(theme_name: str) -> str:
    """生成主题 CSS 样式"""
    t = THEMES.get(theme_name, THEMES["default"])
    is_dark_code = theme_name in ("elegant-black", "geek-green")

    code_block_bg = t["code_bg"]
    code_block_text = t["code_text"] if not is_dark_code else "#abb2bf"

    return f"""
<style>
#gzh-preview {{
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.75;
    color: {t['text']};
    background-color: {t['bg']};
    padding: 20px;
    max-width: 677px;
    margin: 0 auto;
    letter-spacing: 0.5px;
}}

#gzh-preview h1 {{
    font-size: 24px;
    color: {t['primary']};
    text-align: center;
    margin: 30px 0 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid {t['primary']};
    font-weight: 600;
}}

#gzh-preview h2 {{
    font-size: 20px;
    color: {t['primary']};
    margin: 25px 0 15px;
    padding-left: 12px;
    border-left: 4px solid {t['primary']};
    font-weight: 600;
}}

#gzh-preview h3 {{
    font-size: 18px;
    color: {t['text']};
    margin: 20px 0 10px;
    font-weight: 600;
}}

#gzh-preview h4 {{
    font-size: 16px;
    color: {t['text']};
    margin: 18px 0 8px;
    font-weight: 600;
}}

#gzh-preview p {{
    margin: 15px 0;
    text-align: justify;
}}

#gzh-preview blockquote {{
    margin: 15px 0;
    padding: 10px 15px;
    background-color: {t['quote_bg']};
    border-left: 4px solid {t['quote_border']};
    color: {t['text_secondary']};
    font-size: 15px;
    border-radius: 0 4px 4px 0;
}}

#gzh-preview blockquote p {{
    margin: 5px 0;
}}

#gzh-preview code {{
    background-color: {t['code_bg']};
    color: {t['code_text']};
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 14px;
    font-family: "SF Mono", Monaco, Menlo, Consolas, monospace;
}}

#gzh-preview pre {{
    background-color: {code_block_bg};
    border-radius: 5px;
    padding: 15px;
    overflow-x: auto;
    margin: 15px 0;
    font-size: 14px;
    line-height: 1.5;
}}

#gzh-preview pre code {{
    background-color: transparent;
    color: {code_block_text};
    padding: 0;
    font-size: 14px;
}}

#gzh-preview ul, #gzh-preview ol {{
    padding-left: 20px;
    margin: 15px 0;
}}

#gzh-preview li {{
    margin: 8px 0;
}}

#gzh-preview a {{
    color: {t['primary']};
    text-decoration: none;
    border-bottom: 1px solid {t['primary']};
}}

#gzh-preview img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 15px auto;
    display: block;
}}

#gzh-preview table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 15px;
    display: block;
    overflow-x: auto;
}}

#gzh-preview th {{
    background-color: {t['primary']};
    color: #ffffff;
    padding: 10px;
    text-align: left;
    border: 1px solid {t['border']};
}}

#gzh-preview td {{
    padding: 10px;
    border: 1px solid {t['border']};
}}

#gzh-preview tr:nth-child(even) {{
    background-color: {t['quote_bg']};
}}

#gzh-preview hr {{
    border: none;
    border-top: 1px solid {t['border']};
    margin: 25px 0;
}}

#gzh-preview strong {{
    font-weight: 600;
    color: {t['text']};
}}

#gzh-preview em {{
    font-style: italic;
}}

#gzh-preview del {{
    text-decoration: line-through;
    color: {t['text_secondary']};
}}
</style>
"""


# ============================================================
# Markdown 渲染器
# ============================================================


def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return html.escape(text)


def render_inline(text: str) -> str:
    """渲染行内 Markdown 元素"""
    # 行内代码（先处理，避免被其他规则影响）
    text = re.sub(
        r"`([^`]+)`",
        lambda m: f'<code>{escape_html(m.group(1))}</code>',
        text,
    )

    # 图片
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1">',
        text,
    )

    # 链接
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )

    # 加粗
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)

    # 斜体
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"<em>\1</em>", text)

    # 删除线
    text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)

    return text


def render_markdown(md_text: str) -> str:
    """将 Markdown 转换为 HTML"""
    lines = md_text.split("\n")
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 空行
        if not stripped:
            i += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束的 ```
            code_content = escape_html("\n".join(code_lines))
            lang_class = f' class="language-{lang}"' if lang else ""
            html_parts.append(
                f'<pre><code{lang_class}>{code_content}</code></pre>'
            )
            continue

        # 标题
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            content = render_inline(heading_match.group(2))
            html_parts.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # 引用块
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            quote_content = render_inline(" ".join(quote_lines))
            # 处理引用中的段落
            paragraphs = quote_content.split("\n\n")
            quote_html = "".join(f"<p>{p}</p>" for p in paragraphs if p.strip())
            html_parts.append(f"<blockquote>{quote_html}</blockquote>")
            continue

        # 水平线
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            html_parts.append("<hr>")
            i += 1
            continue

        # 无序列表
        if re.match(r"^[-*+]\s+", stripped):
            list_items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i].strip()):
                item_content = re.sub(r"^[-*+]\s+", "", lines[i].strip())
                list_items.append(f"<li>{render_inline(item_content)}</li>")
                i += 1
            html_parts.append(f"<ul>{''.join(list_items)}</ul>")
            continue

        # 有序列表
        if re.match(r"^\d+\.\s+", stripped):
            list_items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item_content = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                list_items.append(f"<li>{render_inline(item_content)}</li>")
                i += 1
            html_parts.append(f"<ol>{''.join(list_items)}</ol>")
            continue

        # 表格
        if "|" in stripped and i + 1 < len(lines) and re.match(
            r"^\|[\s\-:|]+\|$", lines[i + 1].strip()
        ):
            # 解析表头
            headers = [h.strip() for h in stripped.split("|")[1:-1]]
            i += 2  # 跳过分隔行

            # 解析数据行
            rows = []
            while i < len(lines) and "|" in lines[i].strip():
                cells = [c.strip() for c in lines[i].strip().split("|")[1:-1]]
                rows.append(cells)
                i += 1

            # 生成表格 HTML
            thead = "<tr>" + "".join(f"<th>{render_inline(h)}</th>" for h in headers) + "</tr>"
            tbody = ""
            for row in rows:
                tbody += "<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in row) + "</tr>"

            html_parts.append(f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>")
            continue

        # 普通段落
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (
                not next_line
                or next_line.startswith("#")
                or next_line.startswith(">")
                or next_line.startswith("```")
                or next_line.startswith("- ")
                or next_line.startswith("* ")
                or next_line.startswith("+ ")
                or re.match(r"^\d+\.\s+", next_line)
                or re.match(r"^(-{3,}|\*{3,}|_{3,})$", next_line)
            ):
                break
            para_lines.append(next_line)
            i += 1

        para_content = render_inline(" ".join(para_lines))
        html_parts.append(f"<p>{para_content}</p>")

    return "\n".join(html_parts)


# ============================================================
# HTML 模板
# ============================================================


def generate_html(content: str, theme_css: str, custom_css: str = "") -> str:
    """生成完整的 HTML 文档"""
    custom_style = f"<style>{custom_css}</style>" if custom_css else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章预览</title>
    {theme_css}
    {custom_style}
</head>
<body>
<div id="gzh-preview">
{content}
</div>
</body>
</html>"""


# ============================================================
# 主函数
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 转换为微信公众号 HTML"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="输入的 Markdown 文件路径"
    )
    parser.add_argument(
        "-t",
        "--theme",
        default="default",
        choices=list(THEMES.keys()),
        help="主题名称（默认: default）",
    )
    parser.add_argument(
        "--code-theme",
        default="github-light",
        help="代码高亮主题（目前仅记录，样式已内置）",
    )
    parser.add_argument(
        "--custom-css",
        help="自定义 CSS 文件路径（可选）",
    )
    parser.add_argument(
        "-o", "--output", help="输出 HTML 文件路径（默认: 输入文件名.html）"
    )

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    md_content = input_path.read_text(encoding="utf-8")

    # 读取自定义 CSS
    custom_css = ""
    if args.custom_css:
        css_path = Path(args.custom_css)
        if css_path.exists():
            custom_css = css_path.read_text(encoding="utf-8")
        else:
            print(f"警告：自定义 CSS 文件不存在: {args.custom_css}", file=sys.stderr)

    # 渲染
    html_content = render_markdown(md_content)
    theme_css = generate_css(args.theme)
    full_html = generate_html(html_content, theme_css, custom_css)

    # 输出
    output_path = args.output or str(input_path.with_suffix(".html"))
    Path(output_path).write_text(full_html, encoding="utf-8")

    print(f"✅ 渲染完成！")
    print(f"   主题: {args.theme}")
    print(f"   输出: {output_path}")
    print(f"   预览: 在浏览器中打开 {output_path}")


if __name__ == "__main__":
    main()
