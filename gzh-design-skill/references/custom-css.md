# 自定义 CSS 编写指南

本文档介绍如何编写自定义 CSS 来覆盖默认主题样式，实现个性化排版。

## CSS 作用机制

自定义 CSS 会叠加在所选主题之上，优先级高于主题默认样式。使用时通过 `--custom-css` 参数传入：

```bash
python3 scripts/render_gzh.py \
  --input article.md \
  --theme default \
  --custom-css my-style.css \
  --output article.html
```

## 基础结构

公众号文章的 HTML 结构如下，自定义 CSS 基于此结构编写：

```html
<div id="preview">
  <h1>文章标题</h1>
  <h2>章节标题</h2>
  <p>正文段落</p>
  <blockquote>引用内容</blockquote>
  <pre><code>代码块</code></pre>
  <ul><li>列表项</li></ul>
  <table>表格</table>
</div>
```

## 可自定义的样式属性

### 字体设置

```css
/* 正文字体 */
#preview {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", 
               "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.75;
  color: #3f3f3f;
}

/* 标题字体 */
#preview h1, #preview h2, #preview h3 {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-weight: 600;
}
```

### 标题样式

```css
/* H1 主标题 */
#preview h1 {
  font-size: 24px;
  color: #07c160;
  text-align: center;
  margin: 30px 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #07c160;
}

/* H2 章节标题 */
#preview h2 {
  font-size: 20px;
  color: #07c160;
  margin: 25px 0 15px;
  padding-left: 12px;
  border-left: 4px solid #07c160;
}

/* H3 小节标题 */
#preview h3 {
  font-size: 18px;
  color: #333333;
  margin: 20px 0 10px;
}
```

### 段落样式

```css
#preview p {
  margin: 15px 0;
  letter-spacing: 0.5px;
  text-align: justify;
}

/* 首行缩进（如需要） */
#preview p {
  text-indent: 2em;
}
```

### 引用块样式

```css
#preview blockquote {
  margin: 15px 0;
  padding: 10px 15px;
  background-color: #f7f7f7;
  border-left: 4px solid #07c160;
  color: #666666;
  font-size: 15px;
}
```

### 代码样式

```css
/* 行内代码 */
#preview code {
  background-color: #fff0f0;
  color: #c7254e;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 14px;
  font-family: "SF Mono", Monaco, Menlo, Consolas, monospace;
}

/* 代码块 */
#preview pre {
  background-color: #282c34;
  border-radius: 5px;
  padding: 15px;
  overflow-x: auto;
  font-size: 14px;
  line-height: 1.5;
}

#preview pre code {
  background-color: transparent;
  color: #abb2bf;
  padding: 0;
}
```

### 列表样式

```css
/* 无序列表 */
#preview ul {
  padding-left: 20px;
  margin: 15px 0;
}

#preview ul li {
  margin: 8px 0;
}

/* 有序列表 */
#preview ol {
  padding-left: 20px;
  margin: 15px 0;
}
```

### 表格样式

```css
#preview table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 15px;
}

#preview th {
  background-color: #07c160;
  color: #ffffff;
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

#preview td {
  padding: 10px;
  border: 1px solid #ddd;
}

#preview tr:nth-child(even) {
  background-color: #f9f9f9;
}
```

### 图片样式

```css
#preview img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 15px 0;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
```

### 链接样式

```css
#preview a {
  color: #07c160;
  text-decoration: none;
  border-bottom: 1px solid #07c160;
}

#preview a:hover {
  opacity: 0.8;
}
```

## 完整自定义示例

以下是一个完整的自定义 CSS 示例，打造简约文艺风格：

```css
/* 文艺简约风格自定义 CSS */
#preview {
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  line-height: 1.8;
  color: #595959;
  letter-spacing: 0.5px;
}

#preview h1 {
  font-size: 22px;
  color: #8c6a4f;
  text-align: center;
  margin: 35px 0 25px;
  font-weight: 500;
  letter-spacing: 2px;
}

#preview h2 {
  font-size: 18px;
  color: #8c6a4f;
  margin: 30px 0 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e0d5;
  font-weight: 500;
}

#preview h3 {
  font-size: 16px;
  color: #8c6a4f;
  margin: 25px 0 10px;
  font-weight: 500;
}

#preview p {
  margin: 18px 0;
  text-align: justify;
}

#preview blockquote {
  margin: 20px 0;
  padding: 15px 20px;
  background-color: #faf8f5;
  border-left: 3px solid #c4a882;
  color: #8c7853;
  font-style: italic;
}

#preview code {
  background-color: #f5f0e8;
  color: #8c6a4f;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}

#preview pre {
  background-color: #faf8f5;
  border: 1px solid #e8e0d5;
  border-radius: 4px;
  padding: 15px;
  font-size: 13px;
}

#preview pre code {
  background-color: transparent;
  color: #595959;
}

#preview img {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(140, 106, 79, 0.1);
}
```

## CSS 编写注意事项

1. **使用 `#preview` 前缀**：确保样式仅作用于文章内容区域
2. **避免使用 `!important`**：除非必要，否则不建议强制覆盖
3. **移动端适配**：公众号主要在移动端阅读，字号建议不小于 14px
4. **颜色对比度**：确保文字与背景有足够对比度，保证可读性
5. **避免复杂选择器**：公众号编辑器可能会过滤部分复杂 CSS
6. **单位使用**：推荐使用 `px`，避免使用 `em`、`rem`（公众号可能不支持）
