// cos-upload.mjs - 腾讯云 COS 图片上传脚本
// 用法:
//   node cos-upload.mjs <file1> [file2] [file3] ...    上传图片，返回公网 URL
//   node cos-upload.mjs --test                          测试凭证有效性（headBucket）
// 凭证读取自 ~/.workbuddy/cos-config.json

import { readFileSync, statSync } from 'node:fs';
import { resolve, basename, extname } from 'node:path';
import { homedir } from 'node:os';
import { createRequire } from 'node:module';
const CONFIG_PATH = resolve(homedir(), '.workbuddy/cos-config.json');

function loadConfig() {
  try {
    const raw = readFileSync(CONFIG_PATH, 'utf-8');
    return JSON.parse(raw);
  } catch (e) {
    console.error(`❌ 无法读取凭证文件: ${CONFIG_PATH}`);
    console.error('   请确保 ~/.workbuddy/cos-config.json 存在且格式正确');
    process.exit(1);
  }
}

const config = loadConfig();

// 从 node workspace 加载 COS SDK（ESM 不走 NODE_PATH，用 createRequire）
const WORKSPACE_NODE_MODULES = '/Users/lihong/.workbuddy/binaries/node/workspace/node_modules';
const requireFromWorkspace = createRequire(resolve(WORKSPACE_NODE_MODULES, '_'));
const COS = requireFromWorkspace('cos-nodejs-sdk-v5');

const cos = new COS({
  SecretId: config.SecretId,
  SecretKey: config.SecretKey,
});

// 生成唯一 Key：gzh/yyyy-mm-dd/时间戳-原文件名（保留中文）
function makeKey(filename) {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10); // yyyy-mm-dd
  const ts = now.getTime().toString(36); // 短时间戳
  // 保留中文、字母、数字、点、下划线、连字符；其他替换为下划线
  const safeName = basename(filename).replace(/[^\w.\-\u4e00-\u9fa5]/g, '_');
  return `gzh/${dateStr}/${ts}-${safeName}`;
}

// 推断 Content-Type
function getMimeType(ext) {
  const map = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml',
  };
  return map[ext.toLowerCase()] || 'application/octet-stream';
}

async function uploadOne(filePath) {
  const absPath = resolve(filePath);
  try {
    statSync(absPath);
  } catch (e) {
    console.error(`❌ 文件不存在: ${absPath}`);
    return null;
  }

  const ext = extname(absPath);
  const key = makeKey(absPath);
  const mimeType = getMimeType(ext);
  const body = readFileSync(absPath);

  return new Promise((resolvePromise, reject) => {
    cos.putObject({
      Bucket: config.Bucket,
      Region: config.Region,
      Key: key,
      Body: body,
      ContentType: mimeType,
      Headers: {
        'Cache-Control': 'max-age=31536000', // 一年缓存
      },
    }, (err, data) => {
      if (err) {
        console.error(`❌ 上传失败 ${basename(absPath)}: ${err.message || err}`);
        reject(err);
        return;
      }
      const url = `${config.Domain}/${key}`;
      resolvePromise({ file: basename(absPath), key, url, location: data?.Location });
    });
  });
}

async function testConnection() {
  console.log('测试 COS 连接...');
  console.log(`  Bucket: ${config.Bucket}`);
  console.log(`  Region: ${config.Region}`);
  console.log(`  Domain: ${config.Domain}`);
  return new Promise((resolvePromise, reject) => {
    cos.headBucket({
      Bucket: config.Bucket,
      Region: config.Region,
    }, (err, data) => {
      if (err) {
        console.error('❌ 连接失败:', err.message || err);
        console.error('   请检查 SecretId/SecretKey/Bucket/Region 是否正确');
        reject(err);
        return;
      }
      console.log('✅ 凭证有效，存储桶可访问');
      resolvePromise(data);
    });
  });
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`腾讯云 COS 图片上传工具

用法:
  node cos-upload.mjs <file1> [file2] ...   上传图片，输出公网 URL
  node cos-upload.mjs --test                 测试凭证有效性
  node cos-upload.mjs --help                 显示帮助

凭证文件: ~/.workbuddy/cos-config.json
存储路径: gzh/<yyyy-mm-dd>/<时间戳>-<文件名>`);
    return;
  }

  if (args.includes('--test')) {
    await testConnection();
    return;
  }

  const files = args.filter(a => !a.startsWith('-'));
  if (files.length === 0) {
    console.error('❌ 未指定要上传的文件');
    process.exit(1);
  }

  console.log(`上传 ${files.length} 张图片到 COS...\n`);

  const results = [];
  for (const file of files) {
    try {
      const result = await uploadOne(file);
      if (result) {
        results.push(result);
        console.log(`✅ ${result.file}`);
        console.log(`   URL: ${result.url}\n`);
      }
    } catch (e) {
      // 错误已在 uploadOne 中打印
    }
  }

  if (results.length > 0) {
    console.log('=== 上传完成 ===');
    console.log(`成功: ${results.length}/${files.length}`);
    console.log('\n公网 URL 列表:');
    results.forEach(r => console.log(`  ${r.url}`));
  } else {
    console.log('❌ 所有上传均失败');
    process.exit(1);
  }
}

main().catch(e => {
  console.error('❌ 程序异常:', e);
  process.exit(1);
});
