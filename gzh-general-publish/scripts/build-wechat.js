/**
 * 微信公众号 HTML 后处理脚本（通用版）
 * 输入: doocs/md 渲染的 article-preview.html
 * 输出: 微信兼容的 article-wechat-url.html（CSS 内联化 + table 布局 + 渐变修复）
 *
 * 用法: node build-wechat.js <input.html> <output.html>
 * 依赖: juice（NODE_PATH=/Users/lihong/.workbuddy/binaries/node/workspace/node_modules）
 *
 * 注意：图片 URL 应在 Markdown 源中直接用 COS 公网 URL，本脚本不做图片 URL 替换。
 */
const fs = require('fs');
const juiceModule = require('juice');
const juice = juiceModule.juice || juiceModule.default || juiceModule;

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  console.error('用法: node build-wechat.js <input.html> <output.html>');
  process.exit(1);
}

let html = fs.readFileSync(inputPath, 'utf8');
console.log(`输入: ${inputPath} (${(html.length / 1024).toFixed(1)} KB)`);

// === 1. CSS 内联化（微信丢弃 <style> 标签）===
const inlined = juice(html, {
  removeStyleTags: true,
  preserveMediaQueries: false,
  preserveFontFaces: false,
  preserveImportant: true,
  applyStyleTags: true,
});
html = inlined;
console.log('✓ CSS 内联化完成');

// === 2. 删除 doocs 阅读时间块 ===
html = html.replace(
  /<blockquote[^>]*>\s*<p[^>]*>[^<]*\d+\s*words[^<]*min read[^<]*<\/p>\s*<\/blockquote>/gi,
  ''
);
console.log('✓ 删除阅读时间块');

// === 3. 五大模块卡片改 table 布局（微信对 table 兼容最好）===
const modulePattern = /<div class="module-item"[^>]*>\s*<div class="module-num"[^>]*>([^<]+)<\/div>\s*<div class="module-name"[^>]*>([^<]+)<\/div>\s*<\/div>/g;
const modules = [];
let m;
while ((m = modulePattern.exec(html)) !== null) {
  modules.push({ num: m[1].trim(), name: m[2].trim() });
}

if (modules.length === 5) {
  const tdStyle = 'width:50%;height:72px;background:#F5EFE0;border:1px solid #C9B58A;border-radius:6px;padding:12px 8px;text-align:center;vertical-align:middle;box-sizing:border-box;';
  const numStyle = 'font-size:14px;color:#6B4F0E;font-weight:bold;font-family:Georgia,serif;letter-spacing:1px;';
  const nameStyle = 'font-size:14px;color:#3D2E08;font-weight:600;letter-spacing:1px;';

  const makeCell = (num, name, colspan) => {
    const cs = colspan ? ` colspan="${colspan}"` : '';
    return `<td${cs} style="${tdStyle}"><span style="${numStyle}">${num}</span><span style="${nameStyle}">${name}</span></td>`;
  };

  const tableHtml = `<table class="module-grid" style="width:100%;border-collapse:separate;border-spacing:8px;margin:20px 0;table-layout:fixed;">` +
    `<tr>${makeCell(modules[0].num, modules[0].name)}${makeCell(modules[1].num, modules[1].name)}</tr>` +
    `<tr>${makeCell(modules[2].num, modules[2].name)}${makeCell(modules[3].num, modules[3].name)}</tr>` +
    `<tr>${makeCell(modules[4].num, modules[4].name, 2)}</tr>` +
    `</table>`;

  const gridStart = html.indexOf('<div class="module-grid"');
  if (gridStart >= 0) {
    let depth = 0, i = gridStart, gridEnd = -1;
    while (i < html.length) {
      if (html.substr(i, 4) === '<div') depth++;
      else if (html.substr(i, 6) === '</div>') {
        depth--;
        if (depth === 0) { gridEnd = i + 6; break; }
      }
      i++;
    }
    if (gridEnd > gridStart) {
      html = html.slice(0, gridStart) + tableHtml + html.slice(gridEnd);
      console.log(`✓ 五大模块改 table 布局 (${modules.length} 个模块)`);
    }
  }
}

// === 4. 清理微信不支持的 CSS ===
html = html.replace(/box-shadow:[^;"]+;?/gi, '');
// linear-gradient → 纯色 fallback（表头渐变在步骤 6 手动恢复）
html = html.replace(/background:\s*linear-gradient\([^)]+\)/gi, (match) => {
  const colorMatch = match.match(/#[0-9A-Fa-f]{6}/);
  return colorMatch ? `background: ${colorMatch[0]}` : 'background: #F5EFE0';
});
html = html.replace(/@keyframes[^{]*\{[^}]*\}/g, '');
html = html.replace(/animation:[^;"]+;?/gi, '');
console.log('✓ 清理不兼容 CSS');

// === 5. 移除残留 <style> 标签 ===
html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');

// === 6. 特殊图片加内联样式 ===
// 律师头像（圆形 120px）
html = html.replace(
  /(<img[^>]*class="lawyer-avatar-img"[^>]*)(\s*\/?>)/,
  `$1 style="display:block;width:120px !important;height:120px !important;object-fit:cover;border-radius:50% !important;margin:0 auto 16px !important;padding:0 !important;border:3px solid #6B4F0E !important;box-sizing:border-box;"$2`
);
// 二维码（200px）
html = html.replace(
  /(<img[^>]*class="footer-qrcode"[^>]*)(\s*\/?>)/,
  `$1 style="display:block;width:200px !important;height:200px !important;border-radius:4px !important;margin:0 auto !important;padding:0 !important;border:none !important;box-sizing:border-box;"$2`
);
console.log('✓ 特殊图片内联样式');

// === 7. 手动修复表头渐变背景（juice 会把 linear-gradient 降级为纯色）===
// header-inner 深邃蓝色渐变（顶浅底深）
html = html.replace(
  /class="header-inner" style="[^"]*background:\s*#[^;"]+([^"]*)"/,
  `class="header-inner" style="background: linear-gradient(180deg, #F0F5FF 0%, #C8D8EE 25%, #6B8FBF 55%, #2C5286 80%, #1A3A6B 100%);$1"`
);
// header-lightbar 金色光带渐变
html = html.replace(
  /class="header-lightbar" style="[^"]*background:\s*#[^;"]+([^"]*)"/,
  `class="header-lightbar" style="height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(201, 181, 138, 0.3) 25%, #C9B58A 50%, rgba(201, 181, 138, 0.3) 75%, transparent 100%); margin: 0 auto 16px auto;"`
);
// header-logo-img 强制保持原比例（去掉 doocs 加的 max-width 和 width/height 属性）
html = html.replace(
  /(<img[^>]*class="header-logo-img"[^>]*?)\s+width="[^"]*"\s+height="[^"]*"/,
  `$1`
);
html = html.replace(
  /(<img[^>]*class="header-logo-img"[^>]*?)style="([^"]*)"/,
  `$1 style="$2; max-width: 200px !important; width: 200px !important; height: auto !important;"`
);
console.log('✓ 表头渐变背景已手动修复');

fs.writeFileSync(outputPath, html, 'utf8');
console.log(`\n✅ 输出: ${outputPath} (${(html.length / 1024).toFixed(1)} KB)`);
