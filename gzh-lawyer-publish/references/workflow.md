# 工作流详解与踩坑经验

## 完整流程

```
Markdown 源文（图片用 COS URL）
    ↓ doocs/md 渲染 + 自定义 CSS
article-preview.html（带 <style> 标签）
    ↓ build-wechat.js（juice 内联化 + 后处理）
article-wechat-url.html（微信兼容，可直接粘贴）
```

封面和表头动图独立生成，上传 COS 后 URL 嵌入 Markdown。

## 踩坑经验

### 1. 微信粘贴样式丢失
**现象**：浏览器打开 HTML 复制粘贴到公众号编辑器后，样式全乱。
**原因**：doocs/md 渲染输出用 `<style>` 标签 + CSS class，微信粘贴时丢弃整个 `<style>` 标签，只保留 class 名但丢样式。
**解决**：用 juice 库做 CSS inlining，把所有样式写到元素的 `style=""` 属性上。
**注意**：juice 新版用 ES module 导出，需 `const juice = require('juice').default || require('juice')`。

### 2. 图片粘贴不进去
**现象**：base64 内嵌图片粘贴后被微信过滤。
**原因**：微信限制 base64 图片。
**解决**：图片上传到腾讯云 COS（或其他公网图床），用公网 URL。微信粘贴时自动识别外链并转存到微信永久图床。
**注意**：CloudStudio 沙箱站点有时效性，不要用临时站点 URL，用 COS 永久 URL。

### 3. 五大模块卡片大小不一
**现象**：inline-block 布局的卡片宽度错位、换行不一致。
**原因**：inline-block 元素间空白字符影响。
**解决**：改用 table 布局（微信对 table 兼容最好），3行2列，table-layout:fixed，第5个模块 colspan=2。

### 4. 表头渐变丢失
**现象**：CSS 里的 `linear-gradient` 在最终 HTML 里变成纯色。
**原因**：juice 内联时把 `linear-gradient` 解析为纯色 fallback。
**解决**：在 build-wechat.js 中用正则手动恢复渐变。匹配 `class="header-inner" style="...background: #xxx..."` 替换为完整 gradient。

### 5. doocs 给 img 加 max-width 覆盖自定义宽度
**现象**：logo 设 `width:200px` 但显示时被压缩。
**原因**：doocs 渲染时给所有 img 加 `max-width:100%`，覆盖自定义宽度。
**解决**：build-wechat.js 中用 `!important` 强制覆盖，并删除 doocs 加的 `width="200" height="auto"` 属性。

### 6. logo 模糊
**现象**：封面/表头的 logo 看不清。
**原因**：源 logo 分辨率低（如 293×64），放大即糊；或加了 GaussianBlur 发光层。
**解决**：
- 用 LANCZOS 缩放算法
- 加 UnsharpMask 锐化（radius=1, percent=120, threshold=3）
- 不要加 GaussianBlur 发光层（会让 logo 变模糊）
- 表头 GIF 用 2x 渲染再缩小（1280×340 → 640×170）提升清晰度

### 7. PNG 透明通道丢失
**现象**：logo 透明背景变成白色/黑色底。
**原因**：保存时 `final = bg_rgba.convert('RGB')` 把 alpha 通道丢了。
**解决**：直接 `bg_rgba.save(path, 'PNG')`，不要 convert('RGB')。

### 8. logo 原文件无 alpha 通道
**现象**：以为 logo 是透明 PNG，处理时整个矩形被填色。
**原因**：原 PNG 实际无 alpha 透明通道（所有像素 alpha=255），背景是纯白 RGB。
**解决**：按亮度检测（brightness>240）把白色背景设为透明，保留原始 RGB 颜色。

### 9. doocs 渲染脚本不可用
**现象**：`render_gzh.mjs` 报 `Cannot find module` 或 tsx 缺失。
**原因**：doocs/md 是 pnpm monorepo，需要 tsx 运行 TS 模块。
**解决**：
- 方案A：在 doocs-md 根目录 `pnpm --filter @md/mcp-server exec node --import tsx/esm scripts/render_gzh.mjs ...`
- 方案B（推荐）：跳过渲染，用 Python 正则替换 article-preview.html 的第一个 `<style>` 块为新 CSS，再字符串替换图片 alt 文字。

### 10. article-preview.html CSS 固化
**现象**：改了 custom-lawyer.css 但 article-preview.html 里还是旧样式。
**原因**：doocs 渲染时把 CSS 内嵌到 `<style>` 标签，改 CSS 后需重新渲染或手动替换。
**解决**：用 Python `re.sub(r'(<style>\n)([\s\S]*?)(</style>)', ...)` 替换第一个 style 块。

### 11. 微信 1:1 封面裁剪
**现象**：横版封面在微信信息流被裁成 1:1 正方形，中间字看不全。
**解决**：封面用 2×2 田字格四字布局，四个字正好填满上下左右，1:1 裁剪也完整。

### 12. Unicode 圈号字符乱码（重要）
**现象**：五大模块用 `①②③④⑤` 作序号，HTML 源码正常，但粘贴到公众号编辑器后预览时乱码（"开始不乱，一预览就乱"）。
**原因**：`①②③④⑤` 是 Unicode 圈号字符（U+2460-U+2464），公众号编辑器粘贴/预览时编码处理不稳定。
**解决**：序号一律用 ASCII 数字 `01 02 03 04 05`（配合 Georgia serif 字体样式，和章节序号 `01 02 03` 风格统一）。
**禁止**：在公众号 HTML 中使用 `①②③④⑤⑦⑧⑨⑩`、`㈠㈡㈢`、`⑴⑵⑶` 等特殊 Unicode 序号字符。中文标点（·、—、""）可用，但圈号/带圈数字一律避免。

### 13. `<div>` 被微信递归转成 `<section>` 嵌套边框（致命）
**现象**：五大模块卡片区域粘贴后不是正常卡片，而是出现一大堆同心嵌套虚线边框，从外到内缩成一个小点，所有文字和结构都消失。
**原因**：微信编辑器不支持 `<div>` 布局，会把所有 `<div>` 递归转换为 `<section>` 标签，并给每个 `<section>` 自动添加边框样式。`module-grid` → `module-item` → `module-num` 层层嵌套就变成了层层边框。
**解决**：五大模块一律用 `<table>` 布局（微信对 table 支持最好），不要用 `<div>` 模拟网格。`inline-css.js` 和 `build-wechat.js` 都已集成 `div → table` 替换逻辑。
**禁止**：在公众号 HTML 中直接用 `<div class="module-grid">` 包裹多个 `<div class="module-item">` 作为卡片网格布局。

### 14. "第一次预览正常，第二次打开又乱"——微信草稿保存机制（致命）
**现象**：粘贴后第一次预览完全正常，但保存草稿后第二次打开，五大模块（或其他多层 div 区域）变成一层套一层的嵌套虚线边框，内容被挤压消失。
**原因**：微信公众号编辑器有**草稿自动保存机制**——粘贴时保留原始 HTML（所以第一次预览正常），但保存草稿时会运行"标签清理"脚本，把所有 `<div>` 递归转成 `<section>` 并加默认虚线边框。多层嵌套的 div 就变成了多层嵌套的边框。
**解决**：
1. **五大模块用 `<img>` 图片替代**（微信不转换 img）——根治方案。`<table>` 和 `<div>` 在微信草稿保存时都会被递归转换成 `<section>` 并加默认虚线边框。用预生成的 PNG 卡片图（base64 嵌入 `<img>`）可彻底避免此问题。
2. 所有 `<div>` 替换为 `<section>` 标签（微信原生标签）——避免微信草稿保存时重写标签。
3. 给每个 `<section>` 补 `border:none; outline:none; box-sizing:border-box;`，**绝不补 margin:0 / padding:0**——会覆盖原有间距。
4. 需要边框的元素（highlight-box、quote-box、lawyer-card）保留原有 border，只补 `outline:none; box-sizing:border-box;`。
**关键操作**：粘贴新 HTML 前，**必须先删除旧的草稿**，否则微信加载的是旧草稿（已被清理过的乱结构）。
**操作顺序**：有五大模块时，先 `python3 gen-modules-card.py` 生成卡片图 → 再运行 inline-css.js → 粘贴进微信编辑器。

## COS 上传注意事项

- SDK：cos-nodejs-sdk-v5，ESM 加载用 createRequire
- putObject 的 Body 传 readFileSync 结果，不能传 FilePath（会报 missing param Body）
- 存储路径：`gzh/<yyyy-mm-dd>/<时间戳base36>-<原文件名>`（保留中文便于管理）
- 设置一年缓存：Cache-Control: max-age=31536000
- 凭证存 `~/.workbuddy/cos-config.json`（权限 600），不写入 memory 明文

## ImageGen 生成封面背景

用 ImageGen 工具生成深色高级风背景图：
- prompt 示例："Dark premium business background for law firm WeChat article cover, deep navy blue and charcoal gray tones, subtle architectural blueprint lines and legal scales of justice motif, elegant geometric texture overlay, soft gradient lighting, minimalist luxury aesthetic, no text, 16:9 aspect ratio"
- size: 1536x1024
- 生成后用 PIL 裁剪缩放到 900×383（2.35:1），AI 水印会被自然裁掉
