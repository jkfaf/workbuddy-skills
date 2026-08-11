---
name: gzh-design-skill
description: "微信公众号文章排版美化技能，基于 doocs/md (v2.1.x) 开源项目。使用真正的 doocs/md 渲染引擎，将 Markdown 转换为符合微信公众号风格的美观图文。支持 3 种主题（经典/优雅/简洁）、自定义主色调、字体、字号、代码高亮、KaTeX 数学公式、Mermaid 图表、PlantUML、脚注、Ruby 注音、GFM 警告块、自定义 CSS 等完整排版能力。适用于需要为微信公众号撰写并排版文章的场景。触发词：公众号排版、公众号美化、微信文章排版、公众号样式、gzh design、排版公众号、美化公众号文章、微信图文排版、doocs md。"
agent_created: true
---

# 公众号文章排版美化技能（gzh-design-skill）

## 概述

本技能基于开源项目 [doocs/md](https://github.com/doocs/md)（v2.1.x），使用其完整的渲染引擎将 Markdown 转换为微信公众号样式的 HTML。项目源码已下载到 `assets/doocs-md/`，包含完整的渲染核心、主题样式和 MCP Server。

## 适用场景

- 撰写技术博客并发布到微信公众号
- 产品介绍、功能更新的公众号推文排版
- 教程指南类文章的图文混排
- 需要代码高亮、数学公式、流程图的公众号文章
- 将 Markdown 文档快速转换为公众号可粘贴的格式

## 核心能力（doocs/md 引擎）

### 主题系统
| 主题 | 名称 | 风格 |
|------|------|------|
| `default` | 经典 | 简洁清爽，通用场景 |
| `grace` | 优雅 | 优雅美观，适合深度文章 |
| `simple` | 简洁 | 极简风格，聚焦内容 |

### 排版参数
- **主色调**：自定义任意 hex 颜色（默认 `#0F4C81` 经典蓝）
- **字体族**：预设或自定义 CSS font-family
- **字号**：14px-20px 可选
- **代码高亮**：支持 highlight.js 全部主题
- **macOS 代码块**：模拟终端风格的代码块标题栏
- **行号显示**：代码块显示行号
- **引用脚注**：链接转为底部脚注引用
- **阅读时间**：自动计算并显示阅读时间
- **暗色模式**：图表使用暗色配色
- **段首缩进**：段落首行缩进 2em
- **两端对齐**：正文两端对齐
- **标题样式**：每级标题可单独设置样式（default/color-only/border-bottom/border-left/custom）
- **自定义 CSS**：最高优先级的自定义样式

### Markdown 扩展语法
- **KaTeX 数学公式**：行内 `$E=mc^2$`、块级 `$$...$$`
- **Mermaid 图表**：流程图、时序图、甘特图、类图
- **PlantUML**：UML 图表
- **GFM 警告块**：`> [!NOTE]`、`> [!WARNING]`、`> [!TIP]` 等
- **Ruby 注音**：`{漢字|かんじ}` 格式
- **脚注**：标准 Markdown 脚注
- **目录**：`[toc]` 自动生成
- **高亮标记**：`==高亮文字==`
- **滑动块**：`<<< 滑动内容 >>>`

## 使用方式

### 方式一：渲染脚本（推荐）

使用 `scripts/render_gzh.mjs` 直接调用 doocs/md 渲染引擎：

```bash
# 基本用法
cd assets/doocs-md && pnpm --filter @md/mcp-server exec node --import tsx/esm \
  ../../scripts/render_gzh.mjs -i article.md -o output.html

# 指定主题和颜色
pnpm --filter @md/mcp-server exec node --import tsx/esm \
  ../../scripts/render_gzh.mjs -i article.md -t grace --color "#07c160" -o output.html

# 完整参数
pnpm --filter @md/mcp-server exec node --import tsx/esm \
  ../../scripts/render_gzh.mjs \
  -i article.md \
  -t grace \
  --color "#07c160" \
  --font-size 16px \
  --mac-code \
  --line-numbers \
  --count \
  --justify \
  -o output.html

# 自定义 CSS
pnpm --filter @md/mcp-server exec node --import tsx/esm \
  ../../scripts/render_gzh.mjs -i article.md --custom-css my-style.css -o output.html
```

**参数说明：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入 Markdown 文件（必填） | — |
| `-o, --output` | 输出 HTML 文件 | 输入名.html |
| `-t, --theme` | 主题：default/grace/simple | default |
| `--color` | 主色调 hex | #0F4C81 |
| `--font` | 字体族 | 系统默认 |
| `--font-size` | 字号 | 16px |
| `--mac-code` | macOS 风格代码块 | false |
| `--line-numbers` | 代码行号 | false |
| `--cite` | 链接转脚注 | false |
| `--count` | 显示阅读时间 | false |
| `--dark` | 暗色模式 | light |
| `--indent` | 段首缩进 | false |
| `--justify` | 两端对齐 | false |
| `--custom-css` | 自定义 CSS 文件 | — |

### 方式二：MCP Server

doocs/md 提供了 MCP Server，可通过 MCP 协议调用 `render_markdown` 工具。启动方式：

```bash
./scripts/start_mcp_server.sh
```

MCP Server 提供以下工具：
- `render_markdown` — 渲染 Markdown 为 HTML
- `list_themes` — 列出所有主题
- `list_colors` — 列出预设颜色
- `list_fonts` — 列出预设字体
- `list_font_sizes` — 列出预设字号
- `list_legend_formats` — 列出图注格式
- `list_heading_styles` — 列出标题样式
- `list_code_block_themes` — 列出代码高亮主题
- `list_ai_services` — 列出内置 AI 服务
- `explain_extensions` — 解释所有扩展语法
- `get_renderer_options` — 获取渲染器配置说明

### 方式三：在线编辑器

doocs/md 还提供在线编辑器和 CLI 工具：

```bash
# 安装 CLI（全局）
npm i -g @doocs/md-cli

# 启动编辑器（默认端口 8800）
md-cli

# 指定端口
md-cli port=8899
```

或访问在线版：https://md.doocs.org

## 工作流程

### 步骤 1：确认需求
- 文章内容类型（技术、产品、教程等）
- 目标风格（专业、活泼、温暖等）
- 主色调偏好
- 是否需要代码高亮、数学公式、图表等

### 步骤 2：选择主题和参数
参考 `references/themes.md` 了解主题详情，或使用 MCP Server 的 `list_themes`、`list_colors` 等工具查询。

### 步骤 3：渲染
使用 `render_gzh.mjs` 脚本渲染 Markdown 为 HTML。

### 步骤 4：预览与调整
在浏览器中打开 HTML 文件预览效果，调整参数后重新渲染。

### 步骤 5：复制到公众号
1. 浏览器中打开 HTML 文件
2. 全选（Cmd+A）复制（Cmd+C）
3. 粘贴到公众号编辑器（Cmd+V）

## 已知问题与故障排查

### 1. `@md/core` exports 缺失导致渲染失败
**现象**：`render_gzh.mjs` 报错 `Package subpath './theme/cssProcessor' is not defined by "exports"`。

**原因**：`assets/doocs-md/packages/mcp-server/node_modules/@md/core/package.json` 的 `exports` 字段只导出了 `./theme` 和 `./theme/cssVariables`，但 `render-article.ts` 还 import 了 `./theme/cssProcessor` 等子路径。

**修复**：在 `package.json` 的 `exports` 里补全所有 theme 子模块：
```json
"./theme/cssProcessor": "./src/theme/cssProcessor.ts",
"./theme/themeApplicator": "./src/theme/themeApplicator.ts",
"./theme/themeExporter": "./src/theme/themeExporter.ts",
"./theme/themeInjector": "./src/theme/themeInjector.ts",
"./theme/cssScopeWrapper": "./src/theme/cssScopeWrapper.ts",
"./theme/selectorMapping": "./src/theme/selectorMapping.ts"
```

### 2. 微信公众号编辑器粘贴后样式丢失
**现象**：渲染出的 HTML 在浏览器里好看，但粘贴到公众号编辑器后样式全乱。

**原因**：微信编辑器会丢弃 `<style>` 标签，只保留元素的内联 `style` 属性。

**修复**：用 [juice](https://www.npmjs.com/package/juice) 库做 CSS 内联化，把 `<style>` 里的规则合并到元素的 `style` 属性里：
```js
const juice = require('juice');
const inlined = juice(html, { removeStyleTags: true, preserveImportant: true });
```

### 3. base64 图片被微信编辑器过滤
**现象**：图片显示为 `data:image/jpeg;base64,...`，粘贴后图片消失。

**原因**：微信编辑器过滤 base64 图片，只接受公网 URL。

**修复**：将图片上传到公网可访问的静态站点（如 CloudStudio、七牛云、GitHub 图床等），替换为公网 URL。可使用 `workbuddy_cloudstudio_deploy` 工具快速部署图片目录。

### 4. 五大模块卡片 inline-block 宽度错位
**现象**：用 `display: inline-block` 做的网格卡片，粘贴后宽度大小不一。

**原因**：inline-block 元素之间的空白字符（换行、空格）会被渲染为间距，导致宽度计算错位。

**修复**：改用 `<table>` 布局（微信对 table 兼容性最好），固定 `table-layout: fixed` 和 `width: 50%`。

### 5. 字号层次设计建议
公众号文章美观的关键是**字号层次分明**，避免全文几乎一样大：

| 层级 | 元素 | 建议字号 | 角色 |
|------|------|---------|------|
| 装饰大字 | 引号/编号数字 | 28-32px | 视觉锚点 |
| L1 主标题 | h1 | 22px | 明显大于正文 (+6px) |
| L2 章节标题 | 小标题/h2 | 17px | 略大于正文 (+1px, bold) |
| L3 正文 | p | 16px | 基准 |
| L4 设计元素 | 导语/引用/高亮 | 15px | 略小于正文 |
| L5 紧缩元素 | 标签/模块卡片/人名 | 14px | 适度紧缩 |
| L6 明显紧缩 | 简介/联系方式/版尾 | 13px | 明显紧缩 (-3px) |

**反面案例**：标题 20px + 正文 16px（差距仅 4px，标题不够突出）；律师卡片/文末联系都用 15px（与正文 16px 几乎一样，没有紧缩感）。

### 6. 微信不支持的 CSS 特性
粘贴前需清理：`box-shadow`、`linear-gradient`（改为纯色）、`animation`/`@keyframes`、`flex` 布局（部分场景改 table）。

## 资源文件

### scripts/
- `render_gzh.mjs` — Node.js 渲染脚本，直接调用 doocs/md 引擎
- `start_mcp_server.sh` — 启动 MCP Server 的脚本
- `render_gzh.py` — 简化版 Python 渲染器（备用，不依赖 doocs/md）

### references/
- `themes.md` — 主题样式详细说明
- `custom-css.md` — 自定义 CSS 编写指南
- `typography-guide.md` — 公众号排版最佳实践
- `image-hosting.md` — 图床配置指南（13 种图床）

### assets/
- `doocs-md/` — doocs/md 完整项目源码（v2.1.x）
- `css/literary-style.css` — 文艺简约风格自定义 CSS
- `templates/general-template.md` — 通用文章模板
- `templates/tech-article-template.md` — 技术文章模板

## 与其他技能协作

- **wechat-publisher**：本技能负责排版美化，wechat-publisher 负责发布到公众号草稿箱
- **wechat-article-pro**：用于生成长文内容，再用本技能进行排版美化

## 参考项目

- 项目地址：https://github.com/doocs/md
- 在线体验：https://md.doocs.org
- CLI 工具：`npm i -g @doocs/md-cli`
- 感谢项目维护者 yanglbme 及所有贡献者
