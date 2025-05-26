import logging
import os
from datetime import datetime
import sys

# 日志目录路径
LOGS_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# 确保日志目录存在
os.makedirs(LOGS_DATA_DIR, exist_ok=True)

# 获取运行模式
def get_run_mode():
    """根据运行环境确定当前的运行模式"""
    # 检查命令行参数
    if len(sys.argv) > 1 and '--mode' in sys.argv:
        mode_index = sys.argv.index('--mode')
        if mode_index + 1 < len(sys.argv):
            return sys.argv[mode_index + 1]
    
    # 检查调用栈以确定是从哪个模块启动的
    import inspect
    stack = inspect.stack()
    for frame in stack:
        if 'frontend/app.py' in frame.filename:
            return 'frontend'
        elif 'api.py' in frame.filename:
            return 'api'
        elif 'test_' in os.path.basename(frame.filename):
            return 'test'
    
    # 默认模式
    return 'default'

# 创建日志记录器
def get_logger(name, mode=None):
    """获取指定名称和模式的日志记录器
    
    Args:
        name: 日志记录器名称，通常是模块名
        mode: 运行模式，如果为None则自动检测
        
    Returns:
        配置好的日志记录器实例
    """
    # 如果未指定模式，则自动检测
    if mode is None:
        mode = get_run_mode()
    
    # 创建日志文件名，包含模式
    log_file = os.path.join(LOGS_DATA_DIR, f"{mode}.log")
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # 格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
    
    return logger