#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 简化版安装脚本
"""

import subprocess
import sys
import os

def install_simple_requirements():
    """安装简化版所需的依赖包"""
    print("安装基本依赖包...")
    
    # 简化版只需要这些基本库
    requirements = [
        "Pillow",
        "jieba"
    ]
    
    for package in requirements:
        try:
            print(f"正在安装 {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            print(f"✓ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"! {package} 安装时出现问题，但程序可能仍能运行")
    
    print("基本依赖安装完成！")

if __name__ == "__main__":
    print("=" * 50)
    print("小说阅读神器 - 简化版安装程序")
    print("=" * 50)
    
    install_simple_requirements()
    
    print("\n安装完成！现在可以运行程序了：")
    print("python simple_reader.py")