#!/usr/bin/env python3
"""
友小智 - PingPongBuddy 主入口脚本
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 将当前目录添加到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取 API 服务配置
    default_host = os.getenv("API_HOST", "0.0.0.0")
    default_port = int(os.getenv("API_PORT", "8555"))

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="友小智 - PingPongBuddy")
    parser.add_argument('--mode', type=str, default='frontend',
                        choices=['frontend', 'api', 'test'],
                        help='运行模式: frontend(前端界面), api(API服务), test(运行测试)')
    parser.add_argument('--host', type=str, default=default_host,
                        help=f'API服务主机地址 (默认: {default_host}, 可通过环境变量 API_HOST 设置)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'API服务端口 (默认: {default_port}, 可通过环境变量 API_PORT 设置)')
    args = parser.parse_args()
    
    if args.mode == 'frontend':
        # 运行Streamlit前端
        os.system("streamlit run pingpongbuddy/frontend/app.py")
    elif args.mode == 'api':
        # 运行FastAPI服务
        import uvicorn
        print(f"启动 API 服务在 {args.host}:{args.port}...")
        uvicorn.run("pingpongbuddy.api:app", host=args.host, port=args.port, reload=True)
    elif args.mode == 'test':
        # 运行测试
        os.system("python -m unittest discover tests")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 