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
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    if args.mode == 'frontend':
        # 运行Streamlit前端
        os.system("streamlit run pingpongbuddy/frontend/app.py")
    elif args.mode == 'api':
        # 将来支持API模式
        print("API模式尚未实现")
    elif args.mode == 'test':
        # 运行测试
        os.system("python -m unittest discover tests")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 