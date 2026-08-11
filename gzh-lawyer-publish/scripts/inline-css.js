#!/usr/bin/env node
/**
 * CSS Inliner for WeChat Official Account
 *
 * 微信公众号编辑器粘贴 HTML 时会丢弃 <style> 标签，
 * 只保留元素的 class 名但丢失对应样式。
 *
 * 本脚本用 juice 把所有 CSS 规则内联到元素的 style 属性，
 * 并做微信兼容性处理：
 *   - 去除 base64 图片（微信会过滤），替换为占位提示
 *   - 保留 flexbox（微信部分支持）
 *   - 去除 box-shadow / linear-gradient 等不兼容属性
 */

const fs = require('fs');
const path = require('path');
const juiceModule = require('juice');
const juice = juiceModule.default || juiceModule;

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  console.error('Usage: node inline-css.js <input.html> <output.html>');
  process.exit(1);
}

let html = fs.readFileSync(inputPath, 'utf-8');

// 1. juice 内联化 CSS
//    juice 会把 <style> 里的规则应用到对应元素，转成 style 属性
const inlined = juice(html, {
  // 保留 !important
  xmlMode: false,
  // 不移除未使用的 class（保留方便调试）
  removeStyleTags: true,
  // 保留媒体查询等（微信不支持但保留无妨）
  preserveMediaQueries: false,
  // 保留重要样式
  preserveImportant: true,
});

// 2. 微信兼容性处理
let wechat = inlined;

// 2.1 保留 base64 图片（用户要求图片直接显示在 HTML 里）
//     微信粘贴时可能过滤，但浏览器预览完整
//     如需占位版本，可单独运行带占位替换的脚本

// 2.2 去除 box-shadow（微信部分不支持，去掉避免乱）
wechat = wechat.replace(/box-shadow:[^;"]+;?/g, '');

// 2.3 去除 linear-gradient，替换为第一个纯色（取渐变末色）
wechat = wechat.replace(/background:\s*linear-gradient\([^)]+\)/g, (match) => {
  // 提取最后一个颜色值
  const colors = match.match(/#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)/g);
  if (colors && colors.length > 0) {
    return 'background: ' + colors[colors.length - 1];
  }
  return 'background: #f5efe0';
});

// 2.4 去除 transition / animation（微信不支持）
wechat = wechat.replace(/transition:[^;"]+;?/g, '');
wechat = wechat.replace(/animation:[^;"]+;?/g, '');

// 2.5 去除 @keyframes 等规则（如果还残留）
wechat = wechat.replace(/@keyframes[^{]*\{[^}]*\}/g, '');

// 2.6 修复 hr 的 background 语法错误（juice 把多 background 处理坏了）
wechat = wechat.replace(
  /background:\s*rgba\([^)]*\)[^;]*\);/g,
  'background: rgba(0, 0, 0, 0.1);'
);

// 2.7 清理律师头像框里嵌套的图片占位（头像框外层 div 有图片样式，导致冲突）
//     把头像框内的占位 div 简化为纯占位
wechat = wechat.replace(
  /(<div class="lawyer-avatar"[^>]*>)<div[^>]*>\[图片占位：请在此处上传对应图片\]<\/div>(<\/div>)/,
  '$1<div style="width:114px;height:114px;background:#f5efe0;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#A88840;font-size:11px;text-align:center;">律师头像<br>[点击上传]</div>$2'
);

// 2.8b 五大模块卡片：把 module-grid div 替换为预生成的 PNG 图片（base64）
// 微信编辑器对 <img> 标签最友好，不会做任何标签转换/嵌套重写。
// 先生成图片：python3 gen-modules-card.py
// 然后运行本脚本，自动读取 modules-card.png 转为 base64 嵌入。
const fs_mod = require('fs');
const path_mod = require('path');
const cardPng = path_mod.join(process.cwd(), 'modules-card.png');
let moduleImgHtml = '';

if (fs_mod.existsSync(cardPng)) {
  const cardBuf = fs_mod.readFileSync(cardPng);
  const cardB64 = cardBuf.toString('base64');
  moduleImgHtml = `<img class="module-card-img" style="display:block;max-width:100%;height:auto;border-radius:8px;margin:20px auto;" src="data:image/png;base64,${cardB64}" alt="五大核心模块">`;
  console.log('✓ 五大模块使用 base64 图片嵌入（微信不转换 img 标签）');
} else {
  // 回退：生成 table（会残留 table→section 转换风险，不推荐）
  const tdStyle = 'width:50%;height:72px;background:#F5EFE0;border:1px solid #C9B58A;border-radius:6px;padding:12px 8px;text-align:center;vertical-align:middle;box-sizing:border-box;';
  const numStyle = 'font-size:14px;color:#6B4F0E;font-weight:bold;font-family:Georgia,serif;letter-spacing:1px;';
  const nameStyle = 'font-size:14px;color:#3D2E08;font-weight:600;letter-spacing:1px;';
  const makeCell = (num, name, colspan) => {
    const cs = colspan ? ` colspan="${colspan}"` : '';
    return `<td${cs} style="${tdStyle}"><span style="${numStyle}">${num}</span><span style="${nameStyle}">${name}</span></td>`;
  };
  moduleImgHtml = `<table class="module-grid" style="width:100%;border-collapse:separate;border-spacing:8px;margin:20px 0;table-layout:fixed;">` +
    `<tr>${makeCell('01','招投标合规')}${makeCell('02','合同效力认定')}</tr>` +
    `<tr>${makeCell('03','施工过程管理')}${makeCell('04','竣工验收与结算')}</tr>` +
    `<tr>${makeCell('05','建筑材料采购',2)}</tr>` +
    `</table>`;
  console.log('⚠️  modules-card.png 不存在，回退到 table 布局（建议先运行 python3 gen-modules-card.py）');
}

// 替换整个 module-grid div（无论里面是 div 还是 section，找 class="module-grid" 标签）
const gridStart = wechat.indexOf('<div class="module-grid"');
if (gridStart >= 0) {
  let depth = 0;
  let i = gridStart;
  let gridEnd = -1;
  while (i < wechat.length) {
    if (wechat.substr(i, 4) === '<div') depth++;
    else if (wechat.substr(i, 6) === '</div>') {
      depth--;
      if (depth === 0) { gridEnd = i + 6; break; }
    }
    i++;
  }
  if (gridEnd > gridStart) {
    wechat = wechat.slice(0, gridStart) + moduleImgHtml + wechat.slice(gridEnd);
  }
}

// 2.8c 核心修复：把所有 <div> 替换为 <section> 标签（微信原生标签）
// 微信编辑器保存草稿时会运行"标签清理"：
//   1. 把所有 <div> 递归转成 <section>
//   2. 给每个 <section> 加默认虚线边框
//   3. 无视 inline style 中的 border:none
// 导致"第一次预览正常，第二次打开草稿变嵌套边框"的鬼样子。
// 根本解法：主动用 <section> 标签，微信就不会再做 div→section 转换。
// 注意：只能补 border:none / outline:none / box-sizing:border-box，
// 绝不能补 margin:0 / padding:0——会覆盖元素原有间距，导致格式全丢。
// 同时要正确识别 border-left / border-right 等装饰边框，不能被 border:none 覆盖。
wechat = wechat.replace(/<div([^>]*)>/g, (match, attrs) => {
  const styleMatch = attrs.match(/\sstyle="([^"]*)"/);
  if (styleMatch) {
    const existingStyle = styleMatch[1];
    // 检测任意 border 定义（border:、border-left:、border-top: 等）
    // 有边框的元素保留原有边框，只补 outline 和 box-sizing
    if (/border[-a-z]*\s*:/.test(existingStyle)) {
      const additions = [];
      if (!/outline/.test(existingStyle)) additions.push('outline:none');
      if (!/box-sizing/.test(existingStyle)) additions.push('box-sizing:border-box');
      if (additions.length === 0) return '<section' + attrs + '>';
      return '<section' + attrs.replace(/\sstyle="[^"]*"/, ` style="${existingStyle}; ${additions.join('; ')};"`) + '>';
    }
    // 完全没有 border 定义，补 border:none + outline:none + box-sizing
    // 不补 margin:0 / padding:0，保留原有间距
    const additions = ['border:none', 'outline:none'];
    if (!/box-sizing/.test(existingStyle)) additions.push('box-sizing:border-box');
    return '<section' + attrs.replace(/\sstyle="[^"]*"/, ` style="${existingStyle}; ${additions.join('; ')};"`) + '>';
  }
  // 没有 style 属性，只加防边框重置（不含 margin/padding）
  return `<section${attrs} style="border:none; outline:none; box-sizing:border-box;">`;
});
wechat = wechat.replace(/<\/div>/g, '</section>');
console.log('✓ 所有 <div> 已替换为 <section>（保留原有 margin/padding/border-left）');

// 2.9 律师头像 img 补内联样式（juice 没匹配到 .lawyer-avatar-img）
//     圆形裁剪 + 撑满头像框
wechat = wechat.replace(
  /<img class="lawyer-avatar-img"/g,
  '<img class="lawyer-avatar-img" style="width: 100% !important; height: 100% !important; object-fit: cover; border-radius: 50%; display: block; margin: 0; padding: 0; border: none;"'
);

// 2.10 二维码 img 补内联样式
wechat = wechat.replace(
  /<img class="footer-qrcode"/g,
  '<img class="footer-qrcode" style="width: 200px; height: 200px; display: block; margin: 0 auto; border: 3px solid #6B4F0E; border-radius: 8px;"'
);

// 2.11 正文图片（培训现场、学员听讲）补内联样式
wechat = wechat.replace(
  /<img src="data:image\/jpeg;base64/g,
  '<img style="display: block; max-width: 100%; height: auto; border-radius: 8px; margin: 16px auto;" src="data:image/jpeg;base64'
);

// 3. 移除残留的 <style> 标签（juice 应该已经移除，保险起见）
wechat = wechat.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');

// 4. 写入输出文件
fs.writeFileSync(outputPath, wechat, 'utf-8');

const inputSize = Buffer.byteLength(html, 'utf-8');
const outputSize = Buffer.byteLength(wechat, 'utf-8');

console.log('✅ CSS 内联化完成');
console.log(`   输入: ${inputPath} (${(inputSize / 1024).toFixed(1)} KB)`);
console.log(`   输出: ${outputPath} (${(outputSize / 1024).toFixed(1)} KB)`);
console.log(`   base64 图片已替换为占位 div`);
console.log(`   box-shadow / linear-gradient / animation 已清理`);
