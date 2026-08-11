# AI 编排指南：一键发布工作流

## 核心场景

用户发来文章文字 + 图片（本地文件路径），AI 自动完成全部处理，最终输出一个**可直接复制粘贴到公众号后台**的 HTML 文件，并生成封面图和表头动图。

**用户体验**：发文字和图片 → 收到可复制的微信文章 + 封面 + 表头动图。

## AI 自动编排流程（收到用户内容后按此执行）

### 阶段 1：接收与整理

1. 接收用户的文章正文（纯文本或 Markdown）和图片（`@image#1:xxx.jpg` 格式或本地路径）
2. 在当前工作目录创建 `article.md`，把正文整理为标准 Markdown：
   - `#` 一级标题、`##` 二级标题、`**加粗**`、`- 列表`
   - 图片位置先用占位符 `![alt](PLACEHOLDER_1)`，等 COS URL 拿到后替换
   - 律师简介、版尾二维码等用 HTML div + class（见 `css-design.md` 的 class 清单）
3. **对于湖北诚明律师事务所的文章，以下均为固定配置，无需询问：**
   - 表头：固定使用动图 GIF（gen-header-gif.py，律所名"湖 北 诚 明 律 师 事 务 所"）
   - 封面文字：固定田字格四字 **"诚明动态"**
   - 律所 logo：固定 `assets/templates/logo-demo.png`
   - 文末：固定使用下方「湖北诚明律师事务所固定文末模板」
   - 仅当文章涉及特定律师时，才在文末添加 `lawyer-card`（律师简介卡片）

### 阶段 2：图片上传 COS

把用户发来的所有图片上传到腾讯云 COS 获取永久公网 URL：

```bash
# 单张上传（返回公网 URL）
cd ~/.workbuddy/skills/tencent-cos-uploader
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node scripts/cos-upload.mjs <本地图片路径>
```

**批量上传**：可一次传多个文件，脚本会逐张上传并输出 URL。

**URL 格式**：`https://lihong-1323031125.cos.ap-nanjing.myqcloud.com/gzh/<yyyy-mm-dd>/<timestamp>-<文件名>`

拿到 URL 后，替换 `article.md` 中的 `PLACEHOLDER_N` 为真实 COS URL。

### 阶段 3：渲染 Markdown → HTML

**首选**：用 doocs/md 渲染引擎（需要 tsx）：
```bash
cd ~/.workbuddy/skills/gzh-design-skill/assets/doocs-md
pnpm --filter @md/mcp-server exec node --import tsx/esm ../../scripts/render_gzh.mjs \
  -i article.md --custom-css <CSS路径> -o article-preview.html
```

**降级方案**（tsx 不可用时，用正则替换 CSS）：
```python
import re
with open('article-preview.html') as f: html = f.read()
with open('custom-lawyer.css') as f: css = f.read()
# 替换第一个 <style>...</style> 块
new_html = re.sub(r'(<style>\n)([\s\S]*?)(</style>)', r'\g<1>' + css + r'\n\g<3>', html, count=1)
with open('article-preview.html', 'w') as f: f.write(new_html)
```
> 注意：降级方案要求已有渲染好的 HTML 骨架。若完全没有渲染过，需先成功跑通 doocs/md 渲染一次。

### 阶段 4：CSS 内联化 + 微信兼容后处理

```bash
NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules \
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node \
  ~/.workbuddy/skills/gzh-lawyer-publish/scripts/build-wechat.js \
  article-preview.html article-wechat-url.html
```

此脚本一次性完成：juice CSS 内联化、删除阅读时间块、五大模块 table 布局、清理微信不支持的 CSS、手动修复表头渐变。

### 阶段 5：生成封面图

用模板背景图 + 田字格/标题布局生成封面：

```bash
/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  ~/.workbuddy/skills/gzh-lawyer-publish/scripts/gen-cover.py \
  --bg ~/.workbuddy/skills/gzh-lawyer-publish/assets/templates/cover-bg-dark-premium.png \
  --output cover.png \
  --layout tianzi --text "诚明动态" \
  --logo ~/.workbuddy/skills/gzh-lawyer-publish/assets/templates/logo-demo.png
```

**布局选择**：
- `tianzi`：2×2 田字格四字（适合微信 1:1 正方形裁剪，推荐）
- `title`：双行标题 + 副标题（横版 2.35:1）

**背景图**：可用模板 `cover-bg-dark-premium.png`（深色高级风，含法律天平+建工蓝图元素），或用 ImageGen 工具生成新背景。

### 阶段 6：生成表头动图 GIF

```bash
/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  ~/.workbuddy/skills/gzh-lawyer-publish/scripts/gen-header-gif.py \
  --logo ~/.workbuddy/skills/gzh-lawyer-publish/assets/templates/logo-demo.png \
  --output header.gif \
  --firm "湖 北 诚 明 律 师 事 务 所" \
  --en "HUBEI CHENGMING LAW FIRM" \
  --slogan "专 业 · 诚 信 · 高 效"
```

生成 640×170 GIF，36 帧，2.5s 循环：深邃蓝渐变 + 静态 logo + 文字 sin(πt) 淡入淡出 + 柔和金色扫光。

### 阶段 7：上传封面和表头到 COS

```bash
cd ~/.workbuddy/skills/tencent-cos-uploader
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node scripts/cos-upload.mjs cover.png
/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node scripts/cos-upload.mjs header.gif
```

### 阶段 8：替换文章表头为动图

在 `article.md` 顶部，把表头 HTML 替换为 GIF img 标签：
```html
<img src="<表头GIF的COS URL>" alt="律所名" style="width:100%;max-width:640px;display:block;margin:0 auto 28px auto;border-radius:0;" />
```
重新执行阶段 3-4 渲染并构建。

### 阶段 9：呈现结果

用 `present_files` 工具呈现最终产物：
- `article-wechat-url.html`（可复制粘贴的微信文章，浏览器打开全选复制）
- `cover.png`（公众号封面图，上传到公众号后台）
- `header.gif` 的 COS URL（已嵌入文章）

**告诉用户**：浏览器打开 HTML → Cmd+A 全选 → Cmd+C → 粘贴到公众号编辑器。封面图上传到公众号后台。

## 模板资源速查

| 资源 | 路径 | 用途 |
|------|------|------|
| 封面背景图（深色高级风） | `assets/templates/cover-bg-dark-premium.png` | gen-cover.py 的 --bg 参数 |
| 律所 logo | `assets/templates/logo-demo.png` | gen-cover.py 和 gen-header-gif.py 的 --logo 参数 |
| 封面成品示例 | `assets/templates/cover-tianzi-demo.png` | 参考效果 |
| 表头动图成品示例 | `assets/templates/header-animated-demo.gif` | 参考效果 |
| 法律行业 CSS | `assets/custom-lawyer.css` | 渲染时 --custom-css 参数 |

## 环境变量与路径

- Node.js：`/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node`
- Python：`/Users/lihong/.workbuddy/binaries/python/versions/3.13.12/bin/python3`（含 Pillow）
- juice 库：`NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules`
- COS 凭证：`~/.workbuddy/cos-config.json`（权限 600）

## 常见编排决策

1. **用户没发 logo**：用模板 `logo-demo.png`（诚明律所）。若是其他律所，向用户索取。
2. **用户没指定封面文字**：默认田字格"诚明动态"。若是其他文章，根据文章主题提炼四字。
3. **用户没指定配色**：用 `assets/custom-lawyer.css`（深暗金 + 深蓝表头）。若要换色，改 CSS 中的主色变量。
4. **图片是 base64 或本地路径**：必须上传 COS，微信不接受 base64 和本地路径。
5. **粘贴后样式丢失**：确保执行了 build-wechat.js 的 CSS 内联化。
6. **表头渐变变纯色**：build-wechat.js 已含手动修复，无需额外处理。

## 湖北诚明律师事务所 — 固定模板

以下模板用于所有「湖北诚明律师事务所」公众号文章，封面固定"诚明动态"，表头固定动图 GIF，文末固定版尾。

### 固定表头

文章顶部使用 header.gif（gen-header-gif.py 生成），参数固定：
```bash
--firm "湖 北 诚 明 律 师 事 务 所"
--en "HUBEI CHENGMING LAW FIRM"
--slogan "专 业 · 诚 信 · 高 效"
```
在 `article.md` 顶部插入：
```html
<img src="<HEADER_GIF_COS_URL>" alt="湖北诚明律师事务所" style="width:100%;max-width:640px;display:block;margin:0 auto 28px auto;border-radius:0;" />
```

### 固定封面

封面固定田字格四字 **"诚明动态"**：
```bash
--layout tianzi --text "诚明动态"
```

### 固定文末模板

文章正文结束后，按以下结构附加文末（Markdown 中直接写入这些 HTML）：

```
---

<!-- 如有特定律师，在此插入 lawyer-card -->
<div class="lawyer-card">
  <div class="lawyer-avatar">
    <img class="lawyer-avatar-img" src="<律师照片COS_URL>" alt="<律师名>律师" />
  </div>
  <div class="lawyer-name"><律师名> 律师</div>
  <div class="lawyer-title">
    湖北诚明律师事务所<职务><br>
    <专业领域>
  </div>
  <div class="lawyer-divider"></div>
  <div class="lawyer-bio">
    <律师简介文字>
  </div>
</div>

<div class="footer-brand">
  <div class="footer-line"></div>
  <div class="footer-text">湖北诚明律师事务所 · <团队名/领域></div>
  <div class="footer-sub"><品牌slogan></div>
</div>

<div class="gzh-footer">
  <div class="footer-logo">CHENG MING LAW FIRM</div>
  <div class="footer-slogan">
    自诚明谓之性　　自明诚谓之教<br>
    诚则明矣　　　　明则诚矣
  </div>
  <div class="footer-qrcode-wrap">
    <img class="footer-qrcode" src="<公众号二维码COS_URL>" alt="湖北诚明律师事务所微信公众号" />
  </div>
  <div class="footer-qrcode-hint">长按识别二维码，关注「湖北诚明律师事务所」</div>
  <div class="footer-contact-box">
    <div class="footer-contact-title">CONTACT US</div>
    <div class="footer-contact-line">电话：027-82623083 / 82624772</div>
    <div class="footer-contact-line">地址：武汉市江岸区黄孝河路182号竹叶山华中国际广场A栋17层</div>
    <div class="footer-contact-line">网址：www.chengminglawyer.com</div>
  </div>
</div>
```

**注意**：
- 如果用户没有提供公众号二维码图片，文末的 `footer-qrcode` 图片可省略
- `footer-brand` 中的 `<团队名/领域>` 和 `<品牌slogan>` 根据文章内容填写
- 如果文章不涉及特定律师，省略 `lawyer-card` 部分
- 律师没有照片时，省略 `lawyer-avatar`
