---
name: gzh-lawyer-publish
description: "律师事务所/法律行业公众号文章一键排版发布工作流。用户发来文章文字和图片，AI 自动完成：图片上传腾讯云COS图床→Markdown渲染→CSS内联化→生成封面图(田字格/标题布局)→生成表头动图GIF→输出可直接复制粘贴到公众号后台的HTML。整合 gzh-design-skill(doocs/md渲染) 和 tencent-cos-uploader(COS图床) 两个技能。触发词：排版公众号、公众号文章、微信文章排版、律师公众号、律所公众号、诚明动态、公众号封面、表头动图、复制到公众号、粘贴公众号、公众号发布、gzh lawyer。"
agent_created: true
---

# 律师/法律行业公众号文章一键排版发布工作流

## 核心体验

**用户发来文章文字 + 图片 → AI 自动完成全部处理 → 输出可直接复制粘贴到微信公众号后台的 HTML + 封面图 + 表头动图。**

用户只需：
1. 把文章正文（纯文本/Markdown）和图片发给 AI
2. 浏览器打开 AI 生成的 HTML → Cmd+A 全选 → Cmd+C → 粘贴到公众号编辑器
3. 把 AI 生成的封面图上传到公众号后台

## 能力整合（三个 skill 协作）

本 skill 整合了三个 skill 的能力，形成完整工作流：

| 能力 | 来源 skill | 作用 |
|------|-----------|------|
| Markdown → HTML 渲染 | gzh-design-skill（doocs/md 引擎） | 把 Markdown + 自定义 CSS 渲染为美观 HTML |
| 图片上传永久图床 | tencent-cos-uploader（腾讯云 COS） | 把本地图片转为公网 URL，微信不过滤 |
| CSS 内联化 + 微信兼容 | gzh-lawyer-publish（本 skill） | 解决粘贴公众号样式丢失问题 |
| 封面图生成 | gzh-lawyer-publish（本 skill） | PIL 绘制田字格/标题布局封面 |
| 表头动图 GIF | gzh-lawyer-publish（本 skill） | 深邃蓝渐变 + 文字淡入淡出 + 扫光 |

## AI 自动编排流程

**收到用户文字图片后，AI 按 `references/ai-orchestration.md` 自动执行 9 个阶段：**

1. **接收整理**：把正文整理为 Markdown，图片位置用占位符
2. **图片上传 COS**：上传所有图片获取永久公网 URL，替换占位符
3. **渲染 HTML**：doocs/md 渲染 Markdown + CSS（tsx 不可用时降级为正则替换 CSS）
4. **CSS 内联化**：build-wechat.js 完成 juice 内联 + 微信兼容后处理
5. **生成封面图**：gen-cover.py 用模板背景 + 田字格/标题布局
6. **生成表头动图**：gen-header-gif.py 生成 GIF
7. **上传封面表头**：上传到 COS 获取 URL
8. **替换表头**：文章顶部表头 HTML 替换为 GIF img 标签，重新渲染构建
9. **呈现结果**：present_files 呈现可复制 HTML + 封面图 + COS URL

**详细命令和决策规则见 `references/ai-orchestration.md`。**

## 模板资源（开箱即用）

| 资源 | 路径 | 说明 |
|------|------|------|
| 封面背景图（深色高级风） | `assets/templates/cover-bg-dark-premium.png` | 深蓝/深灰，含法律天平+建工蓝图元素，ImageGen 生成 |
| 律所 logo | `assets/templates/logo-demo.png` | 诚明律所原色深蓝 logo（透明 PNG） |
| 封面成品示例 | `assets/templates/cover-tianzi-demo.png` | "诚明动态"田字格封面参考效果 |
| 表头动图成品示例 | `assets/templates/header-animated-demo.gif` | 深邃蓝渐变 + 文字淡入淡出动图参考 |
| 法律行业 CSS | `assets/custom-lawyer.css` | 深暗金正文 + 深蓝渐变表头 + 6 级字号层次 |

## 脚本说明

### scripts/inline-css.js — CSS 内联化 + 微信兼容（含 base64 图片，直接粘贴）
```bash
NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules \
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  scripts/inline-css.js <输入.html> <输出.html>
```
适用于：文章内图片是 base64 格式（直接粘贴进微信编辑器不丢图）。
完成：
- juice CSS 内联化（把 `<style>` 规则内联到各元素 style 属性）
- 去除不兼容属性（box-shadow / linear-gradient / animation / transition）
- **五大模块 `<div>` → base64 PNG 图片替换**（微信编辑器对 `<img>` 完全不转换，根治嵌套边框）
- 全局 `<div>` → `<section>` 标签替换（section 是微信原生标签，不会被重写）
- 保留原有 margin/padding/border-left 等样式（不再覆盖）
- Unicode 圈号 ①→⑤ 兜底替换为 ASCII 数字

**前置步骤**：如果文章有五大模块，先运行 `python3 gen-modules-card.py` 生成卡片图。

### scripts/gen-modules-card.py — 五大模块卡片图生成
```bash
/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  scripts/gen-modules-card.py
```
可选参数（覆盖默认模块内容）：
```bash
python3 gen-modules-card.py "01|模块一" "02|模块二" "03|模块三" "04|模块四" "05|模块五"
```
生成 `modules-card.png`（600×320，2×2+1 卡片布局，深暗金色调）。inline-css.js 会自动读取此图片转为 base64 嵌入，替代微信不兼容的 `<table>` 布局。

### scripts/build-wechat.js — CSS 内联化 + 微信兼容后处理（URL 图片版）
```bash
NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules \
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  scripts/build-wechat.js <输入.html> <输出.html>
```
适用于：文章内图片已是 COS 公网 URL（体积更小，适合已上传图床的场景）。
完成：juice CSS 内联化、删除阅读时间块、五大模块 table 布局、清理不支持 CSS、手动修复表头渐变、替换本地路径为 COS URL。

### scripts/gen-cover.py — 封面图生成（参数化）
```bash
/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3 scripts/gen-cover.py \
  --bg <背景图.png> --output cover.png \
  --layout tianzi --text "诚明动态" --logo <logo.png>
```
布局：`tianzi`（2×2 田字格四字，适合 1:1 裁剪）/ `title`（双行标题+副标题）。画布 900×383（2.35:1）。

### scripts/gen-header-gif.py — 表头动图 GIF（参数化）
```bash
/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3 scripts/gen-header-gif.py \
  --logo <logo.png> --output header.gif \
  --firm "湖 北 诚 明 律 师 事 务 所" --en "HUBEI CHENGMING LAW FIRM" \
  --slogan "专 业 · 诚 信 · 高 效"
```
640×170，36 帧，2.5s 循环：深邃蓝渐变 + 静态 logo + 文字 sin(πt) 淡入淡出 + 柔和金色扫光。2x 渲染再缩放提升清晰度。

## 参考文档

| 文档 | 内容 |
|------|------|
| `references/ai-orchestration.md` | **AI 编排指南**：9 阶段一键发布工作流的详细命令和决策规则 |
| `references/workflow.md` | 踩坑经验：juice 渐变丢失、PNG 透明通道、logo 模糊等 11 条 |
| `references/css-design.md` | CSS 设计规范：配色方案、6 级字号、全部 class 清单 |

## 配色与字号规范

法律行业推荐配色（深暗金正文 + 深蓝渐变表头）：
- 主色 `#6B4F0E`（深暗金，正文强调）
- 表头深蓝渐变 `#F0F5FF → #1A3A6B`（顶浅底深）
- 金色点缀 `#C9B58A`（分隔线、副标语）
- 6 级字号：22px(标题) > 17px(章节) > 16px(正文) > 15px(设计元素) > 14px(模块) > 13px(紧缩)

## 运行环境

- Node.js：`/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node`
- Python：`/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3`（含 Pillow）
- juice 库：`NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules`
- COS 凭证：`~/.workbuddy/cos-config.json`（权限 600）
- doocs/md：`~/.workbuddy/skills/gzh-design-skill/assets/doocs-md/`

## 常见问题

- **粘贴公众号样式丢失** → CSS 必须内联化（build-wechat.js 用 juice）
- **图片粘贴不进去** → 用 COS 公网 URL，不用 base64/本地路径
- **五大模块卡片大小不一** → table 布局替代 inline-block
- **表头渐变变纯色** → build-wechat.js 已含手动正则修复
- **logo 模糊** → 源文件分辨率低，LANCZOS 缩放 + UnsharpMask 锐化，避免 GaussianBlur 发光层
- **PNG 透明通道丢失** → 保存时不要 `.convert('RGB')`，直接 save RGBA
- **封面 1:1 裁剪看不到字** → 用田字格四字布局，居中显示

更多问题见 `references/workflow.md`。
