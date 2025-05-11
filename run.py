#!/usr/bin/env python3
"""
友小智 - PingPongBuddy 主入口脚本
"""

import os
import argparse
from dotenv import load_dotenv

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="友小智 - PingPongBuddy")
    parser.add_argument('--mode', type=str, default='frontend',
                        choices=['frontend', 'api', 'test'],
                        help='运行模式: frontend(前端界面), api(API服务), test(运行测试)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='API服务主机地址')
    parser.add_argument('--port', type=int, default=8000,
                        help='API服务端口')
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
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