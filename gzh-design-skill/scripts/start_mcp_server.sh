#!/bin/bash
# start_mcp_server.sh - 启动 doocs/md MCP Server
#
# 用法:
#   ./start_mcp_server.sh
#
# MCP Server 启动后，可通过 MCP 协议调用 render_markdown 工具
# 将 Markdown 渲染为微信公众号样式的 HTML

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOOCS_MD_DIR="$SCRIPT_DIR/../assets/doocs-md"

cd "$DOOCS_MD_DIR" || {
  echo "错误: 找不到 doocs/md 项目目录: $DOOCS_MD_DIR" >&2
  exit 1
}

exec pnpm --filter @md/mcp-server exec node --import tsx/esm run.mjs
