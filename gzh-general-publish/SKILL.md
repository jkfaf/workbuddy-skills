---
name: gzh-general-publish
description: "通用风格公众号文章一键排版发布工作流。不绑定特定行业，AI 根据文章内容自动选择最合适的配色风格（商务蓝/科技紫/暖橙/极简黑白/文艺墨绿等 6 套预设），或接受用户指定配色。用户发来文章文字和图片，AI 自动完成：图片上传腾讯云COS图床→Markdown渲染→CSS风格自动选择+内联化→生成封面图→生成表头动图GIF→输出可直接复制粘贴到公众号后台的HTML。整合 gzh-design-skill(doocs/md渲染) 和 tencent-cos-uploader(COS图床) 两个技能。触发词：排版公众号、公众号文章、微信文章排版、公众号发布、复制到公众号、粘贴公众号、公众号封面、表头动图、gzh general、通用公众号排版。"
agent_created: true
---

# 通用风格公众号文章一键排版发布工作流

## 核心体验

**用户发来文章文字 + 图片 → AI 自动判断文章风格并选择配色 → 输出可直接复制粘贴到微信公众号后台的 HTML + 封面图 + 表头动图。**

与 `gzh-lawyer-publish`（法律行业专属）的区别：
- **gzh-lawyer-publish**：绑定深暗金 #6B4F0E + 诚明律所 logo/表头，开箱即用
- **gzh-general-publish**（本 skill）：不绑定行业，AI 根据文章内容自动选择 6 套预设风格之一，或接受用户自定义配色

## AI 自动选风格规则

收到文章后，AI 根据内容关键词自动判断：

| 文章类型 | 关键词特征 | 推荐风格 | 预设名 |
|---------|-----------|---------|--------|
| 法律/律所 | 律师、律所、法律、案件、培训 | 深暗金奢华风 | `lawyer-darkgold` |
| 企业/商务 | 公司、企业、管理、战略、会议 | 商务权威风 | `business-blue` |
| 科技/互联网 | 技术、AI、产品、开发、互联网 | 科技现代风 | `tech-purple` |
| 教育/生活 | 教学、学习、课程、亲子、生活 | 暖橙活力风 | `warm-orange` |
| 文化/传统 | 文化、历史、传统、文学、艺术 | 文艺墨绿风 | `literature-green` |
| 通用/文艺 | 任意主题，或用户未指定 | 极简黑白风 | `minimal-black` |

用户也可直接指定风格名或自定义主色，AI 优先遵循用户指令。

## 6 套预设风格速查

| 预设 | 主色 | 浅背景 | 适用场景 |
|------|------|--------|---------|
| `lawyer-darkgold` | #6B4F0E | #F5EFE0 | 法律/律所（深暗金奢华） |
| `business-blue` | #1A3A6B | #F0F5FF | 企业/商务（权威蓝） |
| `tech-purple` | #6B2C91 | #F5F0FA | 科技/互联网（现代紫） |
| `warm-orange` | #D4641E | #FFF5EB | 教育/生活（暖橙活力） |
| `literature-green` | #2D5016 | #F0F5E8 | 文化/传统（墨绿沉稳） |
| `minimal-black` | #2C2C2C | #F8F8F8 | 通用/文艺（极简黑白） |

查看所有预设：`python3 scripts/gen-css.py --list`

## 能力整合（三个 skill 协作）

| 能力 | 来源 skill | 作用 |
|------|-----------|------|
| Markdown → HTML 渲染 | gzh-design-skill（doocs/md 引擎） | 把 Markdown + 自定义 CSS 渲染为美观 HTML |
| 图片上传永久图床 | tencent-cos-uploader（腾讯云 COS） | 把本地图片转为公网 URL，微信不过滤 |
| CSS 风格生成 | gzh-general-publish（本 skill） | 6 套预设 + 自定义配色，参数化生成 CSS |
| CSS 内联化 + 微信兼容 | gzh-general-publish（本 skill） | 解决粘贴公众号样式丢失问题 |
| 封面图生成 | gzh-general-publish（本 skill） | PIL 绘制田字格/标题布局封面 |
| 表头动图 GIF | gzh-general-publish（本 skill） | 渐变背景 + 文字淡入淡出 + 扫光 |

## AI 自动编排流程

**收到用户文字图片后，AI 按 `references/ai-orchestration.md` 自动执行 9 个阶段：**

1. **接收整理**：把正文整理为 Markdown，图片位置用占位符
2. **图片上传 COS**：上传所有图片获取永久公网 URL，替换占位符
3. **选择风格**：AI 根据文章内容选择预设风格，或接受用户指定配色
4. **生成 CSS**：运行 `gen-css.py --preset <风格名>` 生成 CSS
5. **渲染 HTML**：doocs/md 渲染 Markdown + CSS（tsx 不可用时降级为正则替换 CSS）
6. **CSS 内联化**：`inline-css.js` 完成 juice 内联 + div→section + 微信兼容后处理
7. **生成封面图**：`gen-cover.py` 用模板背景 + 田字格/标题布局
8. **生成表头动图**：`gen-header-gif.py` 生成 GIF（参数化 logo/名称/标语）
9. **呈现结果**：上传封面表头到 COS，替换 HTML 中表头，present_files 呈现

**详细命令和决策规则见 `references/ai-orchestration.md`。**

## 脚本说明

### scripts/gen-css.py — CSS 风格生成（核心）
```bash
# 列出所有预设
python3 scripts/gen-css.py --list

# 用预设生成 CSS
python3 scripts/gen-css.py --preset business-blue --output custom.css

# 自定义主色
python3 scripts/gen-css.py --primary #1A3A6B --bg-light #F0F5FF --output custom.css
```

### scripts/inline-css.js — CSS 内联化 + 微信兼容后处理
```bash
NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules \
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  scripts/inline-css.js <输入.html> <输出.html>
```
完成：juice CSS 内联化、div→section 替换（避免微信草稿保存嵌套边框）、五大模块→img 图片替代、Unicode 圈号→ASCII 数字。

### scripts/build-wechat.js — CSS 内联化 + 后处理（备用）
与 inline-css.js 功能类似，含手动修复表头渐变。适用于文章内图片是 URL 格式。

### scripts/gen-cover.py — 封面图生成（参数化）
```bash
python3 scripts/gen-cover.py --bg <背景图> --output cover.png \
  --layout tianzi --text "文章标题" --logo <logo.png>
python3 scripts/gen-cover.py --bg <背景图> --output cover.png \
  --layout title --text "主标题|副标题" --subtitle "作者·日期" --logo <logo.png>
```

### scripts/gen-header-gif.py — 表头动图 GIF 生成（参数化）
```bash
python3 scripts/gen-header-gif.py --logo <logo.png> --output header.gif \
  --firm "机构名称" --en "ENGLISH NAME" --slogan "标 语"
```

### scripts/gen-modules-card.py — 五大模块卡片图生成
```bash
python3 scripts/gen-modules-card.py "01|模块一" "02|模块二" "03|模块三" "04|模块四" "05|模块五"
```

## 预设 CSS 模板

| 文件 | 风格 | 主色 |
|------|------|------|
| `assets/styles/style-lawyer-darkgold.css` | 深暗金奢华风 | #6B4F0E |
| `assets/styles/style-business-blue.css` | 商务权威风 | #1A3A6B |
| `assets/styles/style-tech-purple.css` | 科技现代风 | #6B2C91 |
| `assets/styles/style-warm-orange.css` | 暖橙活力风 | #D4641E |
| `assets/styles/style-minimal-black.css` | 极简黑白风 | #2C2C2C |
| `assets/styles/style-literature-green.css` | 文艺墨绿风 | #2D5016 |

也可用 `gen-css.py` 随时生成新的 CSS，或修改预设后重新生成。

## 参考文档

- `references/ai-orchestration.md` — 9 阶段 AI 编排指南（含风格选择决策规则）
- `references/css-design.md` — CSS 设计指南（6 级字号层次 + HTML 结构模板 + 配色推导规则）
- `references/workflow.md` — 15 条踩坑经验（微信兼容性、COS 上传、PIL 绘图等）

## 依赖

- **gzh-design-skill**（doocs/md 渲染）：`~/.workbuddy/skills/gzh-design-skill/`
- **tencent-cos-uploader**（COS 图床）：`~/.workbuddy/skills/tencent-cos-uploader/`
- **Pillow**（封面/表头/模块卡片生成）：`/Users/lihong/.workbuddy/binaries/python/envs/default/bin/python3`
- **juice**（CSS 内联化）：`/Users/lihong/.workbuddy/binaries/node/workspace/node_modules`

## 与 gzh-lawyer-publish 的关系

| 维度 | gzh-lawyer-publish | gzh-general-publish |
|------|-------------------|-------------------|
| 定位 | 法律行业专属 | 通用，不绑定行业 |
| 配色 | 固定深暗金 #6B4F0E | 6 套预设 + 自定义 |
| 封面 | "诚明动态"田字格 | 参数化，任意文字 |
| 表头 | 诚明律所 logo/名称 | 参数化，任意机构 |
| 模板资源 | 诚明律所专属 | 通用模板 |
| 适用场景 | 律所新闻稿 | 任何公众号文章 |

**推荐用法**：
- 发法律行业文章 → 用 `gzh-lawyer-publish`（开箱即用）
- 发其他风格文章 → 用 `gzh-general-publish`（自动选风格）
