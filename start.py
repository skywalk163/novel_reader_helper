#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 启动脚本
用于快速启动应用程序
"""

import os
import sys
import subprocess

def check_environment():
    """检查环境是否已经安装"""
    try:
        import paddleocr
        import PIL
        import jieba
        return True
    except ImportError:
        return False

def run_installation():
    """运行安装脚本"""
    print("环境未完全安装，正在运行安装脚本...")
    subprocess.call([sys.executable, "install.py"])

def start_application():
    """启动应用程序"""
    print("正在启动小说阅读神器...")
    # subprocess.call([sys.executable, "main.py"])
    subprocess.call([sys.executable, "browser.py"])

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 小说阅读神器 - 启动程序")
    print("=" * 50)
    
    if not check_environment():
        run_installation()
    
    if check_environment():
        start_application()
    else:
        print("❌ 环境安装失败，请手动运行 install.py 并检查错误信息。")
        sys.exit(1)