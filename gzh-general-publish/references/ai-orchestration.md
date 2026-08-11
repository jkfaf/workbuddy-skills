# AI 自动编排指南 — 通用版

## 9 阶段一键发布工作流

收到用户的文章文字 + 图片后，AI 按以下 9 个阶段自动执行：

### 阶段 1：接收整理

**输入**：用户发送的文字（纯文本/Markdown）+ 图片

**AI 操作**：
1. 读取文章文字，整理为标准 Markdown
2. 图片位置用 `![图片说明](占位符)` 标记
3. 识别文章类型（法律/商务/科技/教育/文化/通用），用于阶段 3 选风格
4. 如果用户指定了风格或配色，记录用户偏好

**输出**：`article.md`（整理后的 Markdown）

### 阶段 2：图片上传 COS

**调用**：`tencent-cos-uploader` skill

```bash
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/tencent-cos-uploader/scripts/cos-upload.mjs \
  <图片路径1> [图片路径2] ...
```

**AI 操作**：
1. 提取所有本地图片路径
2. 逐个上传到 COS，获取永久公网 URL
3. 替换 Markdown 中的占位符为 COS URL

**输出**：`article_with_images.md`（图片用 COS URL）

### 阶段 3：选择风格

**AI 决策规则**：

```
如果用户指定了风格名（如"用商务蓝"）→ 用指定预设
否则如果用户指定了主色（如"主色用 #1A3A6B"）→ 自定义配色
否则根据文章内容关键词自动判断：
  - 律师/律所/法律/案件/培训 → lawyer-darkgold
  - 公司/企业/管理/战略/会议 → business-blue
  - 技术/AI/产品/开发/互联网 → tech-purple
  - 教学/学习/课程/亲子/生活 → warm-orange
  - 文化/历史/传统/文学/艺术 → literature-green
  - 其他/不确定 → minimal-black
```

**输出**：确定的风格名（如 `business-blue`）

### 阶段 4：生成 CSS

```bash
/Users/lihong/.workbuddy/binaries/python/envs/default/bin/python3 \
  ~/.workbuddy/skills/gzh-general-publish/scripts/gen-css.py \
  --preset <风格名> --output custom.css
```

或用户自定义配色：
```bash
python3 scripts/gen-css.py --primary #1A3A6B --bg-light #F0F5FF --output custom.css
```

**输出**：`custom.css`（完整 CSS，含 6 级字号层次 + 所有组件样式）

### 阶段 5：渲染 HTML

**调用**：`gzh-design-skill` skill（doocs/md 渲染引擎）

```bash
cd ~/.workbuddy/skills/gzh-design-skill/doocs-md
pnpm --filter @md/mcp-server exec node --import tsx/esm \
  ~/.workbuddy/skills/gzh-design-skill/scripts/render_gzh.mjs \
  <article_with_images.md> <custom.css> <article-preview.html>
```

**降级方案**（tsx 不可用时）：
1. 用 doocs/md 在线版（https://doocs.github.io/md/）手动渲染
2. 或用 Python 正则把 CSS 替换到预渲染 HTML 的 `<style>` 块

**输出**：`article-preview.html`（含 `<style>` 标签的 HTML）

### 阶段 6：CSS 内联化 + 微信兼容后处理

```bash
NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules \
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/gzh-general-publish/scripts/inline-css.js \
  <article-preview.html> <article-wechat.html>
```

**自动完成**：
1. juice CSS 内联化（`<style>` → inline style）
2. div → section 替换（避免微信草稿保存嵌套边框）
3. 五大模块 → img 图片替代（如有 modules-card.png）
4. Unicode 圈号 ①②③ → ASCII 数字 01-05
5. 删除不兼容 CSS（box-shadow、transition、animation）
6. linear-gradient 手动修复（juice 会降级为纯色）

**输出**：`article-wechat.html`（可直接粘贴公众号）

### 阶段 7：生成封面图

```bash
/Users/lihong/.workbuddy/binaries/python/envs/default/bin/python3 \
  ~/.workbuddy/skills/gzh-general-publish/scripts/gen-cover.py \
  --bg <背景图> --output cover.png \
  --layout tianzi --text "文章标题四字" --logo <logo.png>
```

或标题布局：
```bash
python3 scripts/gen-cover.py --bg <背景图> --output cover.png \
  --layout title --text "主标题|副标题" --subtitle "作者·日期" --logo <logo.png>
```

**背景图来源**：
1. 用户提供的图片
2. 或用 ImageGen 生成（参见 workflow.md 的 prompt 模板）
3. 或用预设模板 `assets/templates/cover-bg-dark-premium.png`

**输出**：`cover.png`（900×383 封面图）

### 阶段 8：生成表头动图

```bash
/Users/lihong/.workbuddy/binaries/python/envs/default/bin/python3 \
  ~/.workbuddy/skills/gzh-general-publish/scripts/gen-header-gif.py \
  --logo <logo.png> --output header.gif \
  --firm "机 构 名 称" --en "ENGLISH NAME" --slogan "标 语"
```

**注意**：
- 如果文章没有机构 logo，可省略 `--logo` 参数，用纯文字表头
- 表头渐变色会根据阶段 3 的风格自动匹配（修改 gen-header-gif.py 的 GRADIENT_STOPS）

**输出**：`header.gif`（640×170 动图）

### 阶段 9：上传 + 替换 + 呈现

1. 上传封面和表头到 COS：
```bash
node ~/.workbuddy/skills/tencent-cos-uploader/scripts/cos-upload.mjs \
  cover.png header.gif
```

2. 替换 HTML 中表头为 GIF img 标签

3. 呈现结果：
```
present_files(article-wechat.html, cover.png)
```

**最终输出**：
- `article-wechat.html` — 可直接复制粘贴到公众号
- `cover.png` — 公众号封面图
- COS URL — 封面和表头的永久链接

## 风格选择决策树

```
用户发来文章
    │
    ├─ 用户指定了风格名？ ──→ 用指定预设
    │
    ├─ 用户指定了主色？ ──→ 自定义配色（gen-css.py --primary）
    │
    └─ 自动判断 ──→ 扫描文章关键词
         │
         ├─ 法律类 → lawyer-darkgold
         ├─ 商务类 → business-blue
         ├─ 科技类 → tech-purple
         ├─ 教育类 → warm-orange
         ├─ 文化类 → literature-green
         └─ 其他   → minimal-black
```

## 常见问题处理

### Q: 文章没有 logo 怎么办？
A: 表头省略 `--logo` 参数，用纯文字表头。封面也可省略 logo。

### Q: 文章没有五大模块？
A: `inline-css.js` 检测到没有 `module-grid` div 时会自动跳过模块卡片替换。

### Q: 用户想中途换风格？
A: 重新运行阶段 4（gen-css.py）+ 阶段 5（渲染）+ 阶段 6（内联化），其他阶段不变。

### Q: tsx 不可用无法渲染？
A: 降级方案——用 Python 正则替换预渲染 HTML 的 `<style>` 块为新 CSS，然后直接进入阶段 6。
