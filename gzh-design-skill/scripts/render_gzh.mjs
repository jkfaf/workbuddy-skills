/**
 * render_gzh.mjs - 使用 doocs/md 核心引擎渲染 Markdown 为公众号 HTML
 *
 * 用法:
 *   node render_gzh.mjs --input article.md --theme default --output article.html
 *   node render_gzh.mjs -i article.md -t grace --color "#07c160" -o out.html
 *
 * 需要在 doocs-md 项目目录中运行，或通过 start_mcp_server.sh 调用
 */

import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const SCRIPT_DIR = new URL('./', import.meta.url).pathname
const DOOCS_MD_DIR = resolve(SCRIPT_DIR, '../assets/doocs-md')

// 设置 polyfill（与 MCP Server 的 run.mjs 一致）
function noop() {}
globalThis.MathJax = {
  texReset() {},
  tex2svg(latex) {
    const svgStyle = {}
    const styleProxy = new Proxy(svgStyle, {
      set(_, prop, value) { svgStyle[prop] = value; return true },
      get(_, prop) {
        if (prop === 'setProperty') return (p, v) => { svgStyle[p] = v }
        if (prop === 'display') return svgStyle[prop] || ''
        return svgStyle[prop]
      },
    })
    return {
      firstChild: {
        outerHTML: `<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>${latex.replace(/</g, '&lt;')}</mi></math>`,
        style: styleProxy,
        getAttribute: () => null,
        removeAttribute: noop,
      },
    }
  },
}
globalThis.window = {
  MathJax: globalThis.MathJax,
  addEventListener: noop,
  removeEventListener: noop,
  dispatchEvent: () => true,
  getComputedStyle: () => ({ getPropertyValue: () => '' }),
  requestAnimationFrame: (cb) => setTimeout(cb, 16),
  matchMedia: () => ({ matches: false, addEventListener: noop, removeEventListener: noop }),
}
globalThis.document = {
  getElementById: () => null,
  documentElement: { getAttribute: () => null, style: {} },
  createDocumentFragment: () => ({ appendChild: noop, childNodes: [] }),
  querySelectorAll: () => [],
  querySelector: () => null,
  createElement: (tag) => ({
    tagName: tag.toUpperCase(),
    setAttribute: noop,
    appendChild: noop,
    innerHTML: '',
    style: {},
  }),
  createTextNode: (text) => ({ textContent: text, data: text }),
  body: { appendChild: noop },
  head: { appendChild: noop },
}

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2)
  const opts = {
    input: null,
    output: null,
    theme: 'default',
    color: '#0F4C81',
    fontFamily: null,
    fontSize: null,
    macCodeBlock: false,
    showLineNumber: false,
    citeStatus: false,
    countStatus: false,
    themeMode: 'light',
    useIndent: false,
    useJustify: false,
    customCSS: null,
  }

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '-i':
      case '--input':
        opts.input = args[++i]
        break
      case '-o':
      case '--output':
        opts.output = args[++i]
        break
      case '-t':
      case '--theme':
        opts.theme = args[++i]
        break
      case '--color':
        opts.color = args[++i]
        break
      case '--font':
        opts.fontFamily = args[++i]
        break
      case '--font-size':
        opts.fontSize = args[++i]
        break
      case '--mac-code':
        opts.macCodeBlock = true
        break
      case '--line-numbers':
        opts.showLineNumber = true
        break
      case '--cite':
        opts.citeStatus = true
        break
      case '--count':
        opts.countStatus = true
        break
      case '--dark':
        opts.themeMode = 'dark'
        break
      case '--indent':
        opts.useIndent = true
        break
      case '--justify':
        opts.useJustify = true
        break
      case '--custom-css':
        opts.customCSS = readFileSync(args[++i], 'utf-8')
        break
      case '--help':
      case '-h':
        console.log(`
doocs/md 公众号渲染工具

用法:
  node render_gzh.mjs -i <input.md> [options]

选项:
  -i, --input <file>      输入 Markdown 文件路径（必填）
  -o, --output <file>     输出 HTML 文件路径（默认: 输入名.html）
  -t, --theme <name>      主题: default | grace | simple（默认: default）
  --color <hex>           主色调，如 #07c160（默认: #0F4C81）
  --font <family>         字体族
  --font-size <size>      字号，如 16px
  --mac-code              macOS 风格代码块
  --line-numbers          显示代码行号
  --cite                  链接转为脚注引用
  --count                 显示阅读时间
  --dark                  暗色模式（图表）
  --indent                段首缩进
  --justify               两端对齐
  --custom-css <file>     自定义 CSS 文件
  -h, --help              显示帮助
`)
        process.exit(0)
    }
  }

  if (!opts.input) {
    console.error('错误: 请指定输入文件 (-i <file>)')
    process.exit(1)
  }

  if (!opts.output) {
    opts.output = opts.input.replace(/\.md$/, '.html')
  }

  return opts
}

async function main() {
  const opts = parseArgs()

  // 读取 Markdown 文件
  const markdown = readFileSync(resolve(opts.input), 'utf-8')

  // 动态导入 doocs/md 渲染模块
  process.chdir(DOOCS_MD_DIR)

  const { buildRenderedOutput } = await import(
    pathToFileURL(resolve(DOOCS_MD_DIR, 'packages/mcp-server/src/render-article.ts')).href
  )

  // 调用渲染引擎
  const result = await buildRenderedOutput({
    markdown,
    theme: opts.theme,
    primaryColor: opts.color,
    fontFamily: opts.fontFamily || undefined,
    fontSize: opts.fontSize || undefined,
    isMacCodeBlock: opts.macCodeBlock,
    isShowLineNumber: opts.showLineNumber,
    citeStatus: opts.citeStatus,
    countStatus: opts.countStatus,
    themeMode: opts.themeMode,
    isUseIndent: opts.useIndent,
    isUseJustify: opts.useJustify,
    customCSS: opts.customCSS || undefined,
  })

  // 生成完整 HTML
  const fullHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>微信公众号文章预览</title>
  ${result.html}
</head>
<body>
<div id="preview" style="max-width: 677px; margin: 0 auto; padding: 20px;">
${result.html.includes('<style>') ? '' : ''}
</div>
</body>
</html>`

  // 写入输出文件
  writeFileSync(resolve(opts.output), fullHtml, 'utf-8')

  console.log('✅ 渲染完成！')
  console.log(`   主题: ${opts.theme}`)
  console.log(`   主色: ${opts.color}`)
  console.log(`   字数: ${result.readingTime.words}`)
  console.log(`   预计阅读: ${result.readingTime.minutes} 分钟`)
  console.log(`   输出: ${resolve(opts.output)}`)
}

main().catch((err) => {
  console.error('❌ 渲染失败:', err.message)
  process.exit(1)
})
