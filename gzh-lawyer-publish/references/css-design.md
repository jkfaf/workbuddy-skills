# CSS 设计规范与 class 清单

## 配色方案

### 法律行业推荐：深暗金 + 深蓝表头

| 用途 | 颜色 | 说明 |
|------|------|------|
| 主色（强调、标题） | #6B4F0E | 深暗金，正文 strong/章节标题 |
| 表头深蓝渐变 | #F0F5FF → #1A3A6B | 顶浅底深，专业稳重 |
| 金色点缀 | #C9B58A | 分隔线、副标语、光带 |
| 浅背景 | #F5EFE0 | 导语框、引用块、模块卡片 |
| 边框 | #C9B58A / #A88840 | 卡片边框、分隔线 |
| 深文字 | #3D2E08 | 卡片内深色文字 |
| 浅文字 | #6B5520 | 职务、副标题 |
| 正文 | rgb(62, 62, 62) | 标准正文色 |

### 其他可选配色

| 方案 | 主色 | 风格 |
|------|------|------|
| 藏青权威风 | #003366 | 经典权威，适合国企大客户 |
| 墨绿传统风 | #2D5016 | 沉稳传统，贴合建工领域 |
| 宝蓝现代风 | #0F4C81 | 专业现代，年轻化品牌 |
| 紫罗兰典雅风 | #5B2C6F | 典雅独特，差异化路线 |

## 6 级字号层次

法律文章层次分明，避免"全文字号一样"的扁平感：

| 层级 | 元素 | 字号 | 角色 |
|------|------|------|------|
| 装饰大字 | quote-mark / section-num | 32/28px | 视觉锚点 |
| L1 主标题 | h1 | 22px | 明显大于正文 (+6px) |
| L2 章节标题 | section-text / h2 | 17px | 略大于正文 (+1px, bold) |
| L3 正文 | p | 16px | 基准 |
| L4 设计元素 | lead-content / quote-text / highlight-box | 15px | 略小于正文 |
| L5 紧缩元素 | lead-label / module-num/name / lawyer-name | 14px | 适度紧缩 |
| L6 明显紧缩 | lawyer-title/bio / footer 全部 | 13px | 明显紧缩 (-3px) |

## CSS class 清单（Markdown 中可用 HTML div）

### 导语框
```html
<div class="lead-box">
<span class="lead-label">导语</span>
<div class="lead-content">导语内容...</div>
</div>
```

### 编号小标题
```html
<div class="section-title">
<span class="section-num">01</span>
<span class="section-text">章节标题</span>
</div>
```

### 引用块
```html
<div class="quote-box">
<div class="quote-mark">"</div>
<div class="quote-text">引用金句</div>
<div class="quote-sub">副标语</div>
</div>
```

### 五大模块卡片（build-wechat.js 自动转 table）
```html
<div class="module-grid">
<div class="module-item">
<div class="module-num">01</div>
<div class="module-name">模块名</div>
</div>
<!-- 重复 5 个，序号用 01-05（禁止用①②③④⑤，微信预览乱码） -->
</div>
```

### 重点高亮框
```html
<div class="highlight-box">
重点内容，**加粗**会变主题色
</div>
```

### 律师卡片
```html
<div class="lawyer-card">
<div class="lawyer-avatar">
<img class="lawyer-avatar-img" src="证件照URL" alt="律师名" />
</div>
<div class="lawyer-name">姓名 律师</div>
<div class="lawyer-title">职务<br>专业领域</div>
<div class="lawyer-divider"></div>
<div class="lawyer-bio">简介内容...</div>
</div>
```

### 页脚品牌区
```html
<div class="footer-brand">
<div class="footer-line"></div>
<div class="footer-text">律所名 · 团队名</div>
<div class="footer-sub">标语</div>
</div>
```

### 公众号版尾（二维码+联系信息）
```html
<div class="gzh-footer">
<div class="footer-logo">英文名</div>
<div class="footer-slogan">中文标语</div>
<div class="footer-qrcode-wrap">
<img class="footer-qrcode" src="二维码URL" alt="公众号" />
</div>
<div class="footer-qrcode-hint">长按识别二维码</div>
<div class="footer-contact-box">
<div class="footer-contact-title">CONTACT US</div>
<div class="footer-contact-line">电话：xxx</div>
<div class="footer-contact-line">地址：xxx</div>
</div>
</div>
```

### 图片 figure + figcaption（doocs 自动生成）
```markdown
![图片说明](图片URL)
```
doocs 自动转为 `<figure><img><figcaption>图片说明</figcaption></figure>`，CSS 控制 figure 宽度 90% 居中、figcaption 浅灰居中。

## 表头 HTML 结构（若不用动图）

```html
<div class="article-header">
<div class="header-frame">
<div class="header-inner">
<div class="header-lightbar"></div>
<div class="header-logo-wrap">
<img class="header-logo-img" src="logoURL" alt="律所名" />
</div>
<div class="header-title">律 所 中 文 名</div>
<div class="header-en">ENGLISH NAME</div>
<div class="header-divider"></div>
<div class="header-slogan">副 · 标 · 语</div>
</div>
</div>
</div>
```

若用动图，直接用 img 标签替换整个表头：
```html
<img src="表头GIF的URL" alt="律所名" style="width:100%;max-width:640px;display:block;margin:0 auto 28px auto;border-radius:0;" />
```

## 关键 CSS 属性（微信兼容）

- 字体：`"PingFang SC", -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", sans-serif`
- 行高：1.8（正文）/ 1.5（标题）/ 1.7（小字）
- 字间距：1px（正文）/ 2px（强调）/ 5-6px（装饰大字）
- 对齐：justify（正文）/ center（标题、卡片）
- 不支持：box-shadow、animation、flex（用 table 替代）、linear-gradient（需手动修复）
