---
name: tencent-cos-uploader
description: "腾讯云 COS 图片上传技能。将本地图片上传到用户的腾讯云 COS 存储桶，返回永久公网 URL。适用于公众号排版、博客写作、文档配图等需要图片托管场景。触发词：上传图片、图床、COS、腾讯云存储、图片URL、图片托管、传到图床、上传到COS、获取图片链接、图片公网地址。"
agent_created: true
---

# 腾讯云 COS 图片上传技能（tencent-cos-uploader）

## 概述

将本地图片上传到用户的腾讯云 COS 存储桶，返回永久公网 URL。解决公众号排版、文档配图等场景下图片需要公网可访问 URL 的需求。

## 适用场景

- 公众号文章排版（配合 gzh-design-skill）
- 博客/文档配图需要公网 URL
- 用户发来图片，需要获取可引用的公网链接
- 替代临时图床（如 CloudStudio 沙箱站点），使用用户自己的永久图床

## 凭证配置

凭证文件位置：`~/.workbuddy/cos-config.json`（权限 600，仅 owner 可读写）

```json
{
  "SecretId": "AKIDxxxxxxxx",
  "SecretKey": "xxxxxxxxxxxx",
  "Bucket": "bucket-name-appid",
  "Region": "ap-nanjing",
  "Domain": "https://bucket-name-appid.cos.region.myqcloud.com"
}
```

**凭证不存在时**：向用户索取腾讯云 COS 的 SecretId / SecretKey / Bucket / Region，写入配置文件后 chmod 600。

**安全规则**：
- 永远不要把凭证明文写入 memory.md / SKILL.md / 日志
- 不要在回复中回显完整 SecretKey
- 凭证文件权限必须 600

## 使用方式

### 方式一：命令行上传

```bash
# 单张上传
node scripts/cos-upload.mjs /path/to/image.jpg

# 批量上传
node scripts/cos-upload.mjs img1.jpg img2.jpg img3.jpg

# 测试凭证
node scripts/cos-upload.mjs --test
```

**运行环境**：
- Node.js：`/Users/lihong/.workbuddy/binaries/node/versions/22.22.2/bin/node`
- COS SDK：`/Users/lihong/.workbuddy/binaries/node/workspace/node_modules`（已安装 cos-nodejs-sdk-v5）
- 脚本通过 `createRequire` 从 workspace 加载 SDK，无需 NODE_PATH

### 方式二：用户发图时自动上传

当用户在对话中发送图片（如 `@image#1:xxx.jpg`）并需要公网 URL 时：
1. 找到图片在本地文件系统的路径（通常在临时目录或用户指定目录）
2. 调用 `cos-upload.mjs` 上传
3. 把返回的公网 URL 用于文章、文档等

## 存储路径规则

```
gzh/<yyyy-mm-dd>/<时间戳base36>-<原文件名>
```

示例：`gzh/2026-07-19/mrr9vyiv-培训现场全景.jpg`

- 按日期分目录，便于管理
- 时间戳 base36 编码，保证唯一性
- 保留中文文件名（COS Key 支持 UTF-8）
- 设置一年缓存（Cache-Control: max-age=31536000）

## 公网 URL 格式

```
https://<bucket>.cos.<region>.myqcloud.com/gzh/<date>/<timestamp>-<name>.<ext>
```

示例：
```
https://lihong-1323031125.cos.ap-nanjing.myqcloud.com/gzh/2026-07-19/mrr9vyiv-培训现场全景.jpg
```

## 资源文件

### scripts/
- `cos-upload.mjs` — 上传脚本，支持单张/批量上传、--test 测试凭证、--help 帮助

## 与其他技能协作

- **gzh-design-skill**：公众号排版时，文章图片应上传到 COS 获取永久 URL，避免使用临时图床（CloudStudio 沙箱有时效性）
- **wechat-publisher**：发布到公众号前，确保所有图片已是 COS 永久 URL

## 故障排查

### 1. `Cannot find package 'cos-nodejs-sdk-v5'`
脚本用 `createRequire` 从 `/Users/lihong/.workbuddy/binaries/node/workspace/node_modules` 加载 SDK。如果缺失：
```bash
cd /Users/lihong/.workbuddy/binaries/node/workspace && npm install cos-nodejs-sdk-v5
```

### 2. `missing param Body`
`cos.putObject` 必须传 `Body`（Buffer），不能用 `FilePath`。脚本已用 `readFileSync` 读取文件内容作为 Body。

### 3. `403 Forbidden` 或 `key not exist`
检查凭证是否正确：`node cos-upload.mjs --test`

### 4. URL 访问返回 403
存储桶权限需设为「公有读私有写」。在 COS 控制台 → 权限管理 → 存储桶访问权限，设为「公有读私有写」。

## 参考文档

- 腾讯云 COS 文档：https://cloud.tencent.com/document/product/436
- cos-nodejs-sdk-v5：https://github.com/tencentyun/cos-nodejs-sdk-v5
