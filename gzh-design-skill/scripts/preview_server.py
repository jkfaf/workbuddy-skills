#!/usr/bin/env python3
"""
preview_server.py - 本地预览服务器

启动一个本地 HTTP 服务器，预览公众号文章排版效果。
支持文件监听自动刷新（需要 watchdog 库，未安装时自动降级）。

用法:
    python3 preview_server.py --file article.html --port 8080
    python3 preview_server.py -f article.html -p 8080 --watch
"""

import argparse
import http.server
import socketserver
import os
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器，添加 CORS 和无缓存头"""

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        sys.stderr.write(f"\r[{time.strftime('%H:%M:%S')}] {args[0]}\n")


if HAS_WATCHDOG:

    class FileWatcher(FileSystemEventHandler):
        """监听文件变化"""

        def __init__(self, callback):
            self.callback = callback
            self.last_modified = 0

        def on_modified(self, event):
            if event.is_directory:
                return

            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time

            print(f"\n📄 检测到文件变化: {event.src_path}")
            self.callback(event.src_path)


def start_server(port: int, directory: str):
    """启动 HTTP 服务器"""
    os.chdir(directory)

    handler = PreviewHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 预览服务器已启动")
            print(f"   地址: http://localhost:{port}")
            print(f"   目录: {directory}")
            print(f"   按 Ctrl+C 停止\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except OSError as e:
        if e.errno == 48:
            print(f"❌ 端口 {port} 已被占用，请使用其他端口")
            print(f"   尝试: python3 preview_server.py --port {port + 1}")
        else:
            print(f"❌ 启动失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="公众号文章预览服务器")
    parser.add_argument("-f", "--file", help="要预览的 HTML 文件路径")
    parser.add_argument("-d", "--directory", help="服务器根目录（默认: 文件所在目录）")
    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="服务器端口（默认: 8080）"
    )
    parser.add_argument(
        "--watch", action="store_true", help="监听文件变化（需要 watchdog 库）"
    )

    args = parser.parse_args()

    if args.directory:
        directory = args.directory
    elif args.file:
        directory = str(Path(args.file).parent.resolve())
    else:
        directory = os.getcwd()

    if args.file:
        filename = Path(args.file).name
        file_url = f"http://localhost:{args.port}/{filename}"
        print(f"📄 预览文件: {file_url}")

    if args.watch and args.file:
        if not HAS_WATCHDOG:
            print("⚠️  未安装 watchdog 库，文件监听功能不可用")
            print("   安装: pip install watchdog")
            print("   将使用手动刷新模式\n")
        else:
            watch_path = str(Path(args.file).parent.resolve())
            observer = Observer()
            event_handler = FileWatcher(
                lambda f: print("   请刷新浏览器查看更新")
            )
            observer.schedule(event_handler, watch_path, recursive=False)
            observer.start()
            print(f"👁️  正在监听文件变化: {watch_path}")

    start_server(args.port, directory)


if __name__ == "__main__":
    main()
