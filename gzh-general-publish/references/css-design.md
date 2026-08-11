# CSS 设计指南 — 通用版

## 6 级字号层次（核心设计原则）

所有风格共用同一套字号层次，保证排版美观一致：

| 层级 | 元素 | 字号 | 角色 | 字重 |
|------|------|------|------|------|
| L1 主标题 | h1 | **22px** | 明显大于正文 (+6px) | bold |
| L2 章节标题 | h2 / section-text | **17px** | 略大于正文 (+1px) | bold |
| L3 正文 | p | **16px** | 基准 | normal |
| L4 设计元素 | lead-content / quote-text / highlight-box | **15px** | 略小于正文 (-1px) | normal |
| L5 紧缩元素 | lead-label / quote-sub / module-num/name / lawyer-name | **14px** | 适度紧缩 (-2px) | bold/normal |
| L6 明显紧缩 | lawyer-title/bio / footer / gzh-footer | **13px** | 明显紧缩 (-3px) | normal |

**关键原则**：
- h1 必须明显大于正文（至少 +6px），否则标题感不足
- 设计元素（导语/引用/高亮）略小于正文，形成层次
- 版尾/卡片次要信息明显紧缩，不喧宾夺主

## 6 套预设配色方案

### 1. lawyer-darkgold — 深暗金奢华风（法律行业）

| 色彩角色 | 色值 | 用途 |
|---------|------|------|
| 主色 primary | #6B4F0E | h2 标题、边框、装饰 |
| 浅背景 bg_light | #F5EFE0 | 导语框、高亮框背景 |
| 卡片背景 bg_card | #EDE3CC | 引用块背景 |
| 装饰边框 border_decor | #C9B58A | 引用块虚线边框 |
| 中间色 middle | #A88840 | 章节序号、装饰大字 |
| 深文字 text_dark | #3D2E08 | 导语/引用文字 |
| 浅文字 text_light | #6B5520 | 副标题、职务 |
| 表头渐变 | #F0F5FF → #1A3A6B | 顶浅底深深邃蓝 |

### 2. business-blue — 商务权威风（企业/商务）

| 色彩角色 | 色值 |
|---------|------|
| primary | #1A3A6B |
| bg_light | #F0F5FF |
| bg_card | #E0EAF7 |
| border_decor | #9DB8D6 |
| middle | #5A7FA8 |
| text_dark | #1A2C4A |
| text_light | #3A5070 |

### 3. tech-purple — 科技现代风（科技/互联网）

| 色彩角色 | 色值 |
|---------|------|
| primary | #6B2C91 |
| bg_light | #F5F0FA |
| bg_card | #E8DCEF |
| border_decor | #B894C9 |
| middle | #8B6BA8 |
| text_dark | #2C1A3D |
| text_light | #4A3A5C |

### 4. warm-orange — 暖橙活力风（教育/生活）

| 色彩角色 | 色值 |
|---------|------|
| primary | #D4641E |
| bg_light | #FFF5EB |
| bg_card | #FFE8D1 |
| border_decor | #F0B888 |
| middle | #C08850 |
| text_dark | #3D2A0E |
| text_light | #6B4A20 |

### 5. minimal-black — 极简黑白风（通用/文艺）

| 色彩角色 | 色值 |
|---------|------|
| primary | #2C2C2C |
| bg_light | #F8F8F8 |
| bg_card | #EEEEEE |
| border_decor | #CCCCCC |
| middle | #888888 |
| text_dark | #1A1A1A |
| text_light | #555555 |

### 6. literature-green — 文艺墨绿风（文化/传统）

| 色彩角色 | 色值 |
|---------|------|
| primary | #2D5016 |
| bg_light | #F0F5E8 |
| bg_card | #DCE8C8 |
| border_decor | #A8C088 |
| middle | #6B8B4A |
| text_dark | #1A2C0E |
| text_light | #3A5020 |

## 配色推导规则（自定义配色时）

如果用户指定主色但未指定其他色，按以下规则自动推导：

| 色彩角色 | 推导规则 | 示例（主色 #1A3A6B） |
|---------|---------|---------------------|
| primary_light | 主色提亮 20% | #2C5286 |
| bg_light | 主色 + 90% 白色混合 | #F0F5FF |
| bg_card | 主色 + 80% 白色混合 | #E0EAF7 |
| border_decor | 主色 + 60% 白色混合 | #9DB8D6 |
| middle | 主色 + 50% 白色混合 | #5A7FA8 |
| text_dark | 主色 + 10% 黑色混合 | #1A2C4A |
| text_light | 主色 + 30% 白色混合 | #3A5070 |

## HTML 结构模板

### 标准文章结构

```html
<!-- 表头动图 -->
<img src="header.gif" style="width:100%;border-radius:8px;margin-bottom:20px;">

<!-- h1 主标题 -->
<h1>文章标题</h1>

<!-- 导语框 -->
<div class="lead-box">
  <span class="lead-label">导语</span>
  <p class="lead-content">导语内容，概述文章要点...</p>
</div>

<!-- 正文段落 -->
<p>正文内容...</p>

<!-- 章节标题（带序号） -->
<div class="section-title">
  <span class="section-num">01</span>
  <span class="section-text">章节标题</span>
</div>

<!-- 正文 + 图片 -->
<p>段落内容...</p>
<figure>
  <img src="图片URL" alt="图片说明">
  <figcaption>图片说明文字</figcaption>
</figure>

<!-- 引用块 -->
<div class="quote-box">
  <div class="quote-mark">"</div>
  <p class="quote-text">引用内容...</p>
  <p class="quote-sub">—— 引用来源</p>
</div>

<!-- 高亮框 -->
<div class="highlight-box">
  <p>重点提示内容...</p>
</div>

<!-- 作者/人物卡片 -->
<div class="lawyer-card">
  <img class="lawyer-avatar" src="头像URL">
  <div class="lawyer-info">
    <p class="lawyer-name">姓名</p>
    <p class="lawyer-title">职务</p>
    <p class="lawyer-bio">简介...</p>
  </div>
</div>

<!-- 分隔线 -->
<hr>

<!-- 版尾卡片 -->
<div class="gzh-footer">
  <p class="gzh-footer-name">机构名称</p>
  <p class="gzh-footer-slogan">标语</p>
  <img class="gzh-footer-qrcode" src="二维码URL">
  <p class="gzh-footer-tip">长按识别二维码关注</p>
</div>
```

## 微信兼容性注意事项

1. **禁止 Unicode 序号字符**：`①②③④⑤`、`㈠㈡㈢`、`⑴⑵⑶` 在公众号预览时乱码，一律用 ASCII 数字 `01 02 03`
2. **CSS 必须内联化**：微信丢弃 `<style>` 标签，用 juice 内联
3. **div → section 替换**：微信草稿保存时把 `<div>` 递归转成 `<section>` 并加边框，主动用 `<section>` 避免
4. **五大模块用 img 替代**：`<table>` 的 `<td>` 也会被微信转换，用 PIL 生成 PNG 图片嵌入 `<img>` 是根治方案
5. **linear-gradient 需手动修复**：juice 内联时把渐变降级为纯色，需在 build-wechat.js 中手动修复
6. **box-shadow 部分不支持**：删除或用 border 替代
7. **flex 布局兼容性差**：改用 inline-block 或 table
8. **中文标点可用**：`·`、`—`、`""` 等中文标点在公众号正常显示
