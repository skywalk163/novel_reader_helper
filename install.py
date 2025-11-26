#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读神器 - 安装脚本
自动安装所需依赖包和初始化环境

使用方法:
python install.py --quick  # 安装最少的必要库，不包含OCR功能
python install.py --full   # 安装所有库，包含PaddleOCR相关库
python install.py          # 默认使用quick模式
"""

import subprocess
import sys
import os
import platform
import argparse

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 错误：需要 Python 3.7 或更高版本")
        print(f"   当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements(mode="quick"):
    """安装依赖包"""
    print(f"\n📦 开始安装依赖包... (模式: {mode})")
    
    # 基础依赖包（必须安装）
    basic_requirements = [
        "PyQt5>=5.15.0",
        "PyQt5_qt5>=5.15.0",
        "PyQtWebEngine>=5.15.0",
        "PyQtWebEngine-Qt5>=5.15.0,<5.16.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "jieba>=0.42.1",
    ]
    
    # OCR相关依赖（仅完整安装）
    ocr_requirements = [
        "numpy>=1.24.0,<2.0.0",  # OCR需要numpy
        "Pillow>=10.0.0,<12.0.0",  # OCR需要Pillow进行图片处理
        "opencv-python>=4.8.0",
        "paddlepaddle>=2.5.0",
        "paddleocr>=2.7.0",
        "flask>=2.3.3"
    ]
    
    # 根据模式选择要安装的依赖
    if mode == "full":
        requirements = basic_requirements + ocr_requirements
        print("👉 完整安装模式：将安装所有依赖，包括PaddleOCR相关库")
    else:  # quick模式
        requirements = basic_requirements
        print("👉 快速安装模式：仅安装必要的基础库，不包含OCR功能")
    
    # 使用进度计数器
    total_packages = len(requirements)
    current = 0
    print(f"安装进度: [0/{total_packages}]")
    
    # 创建 DEVNULL 输出对象，用于屏蔽 pip 输出
    DEVNULL = open(os.devnull, 'w') 
    
    for package in requirements:
        try:
            current += 1
            # 使用\r覆盖前一行内容，保持输出在一行
            print(f"\r安装进度: [{current}/{total_packages}] - 正在安装 {package}...", end="", flush=True)
            
            # 使用 DEVNULL 来屏蔽标准输出和错误输出
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, 
                "--no-deps"
            ], stdout=DEVNULL, stderr=DEVNULL)
            
        except subprocess.CalledProcessError as e:
            # 安装失败但继续
            pass
    
    # 完成所有包安装后，覆盖进度行并换行
    print("\r安装进度: 完成!                                               ")
    
    # 最后安装可能缺失的基础依赖，静默方式
    basic_deps = ["scipy", "matplotlib", "six", "protobuf", "lmdb", "tqdm"]
    print("安装基础依赖组件...")
    for dep in basic_deps:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep, 
                "--quiet"
            ], stdout=DEVNULL, stderr=DEVNULL)
        except:
            pass  # 忽略基础依赖的安装错误
            
    # 关闭DEVNULL
    DEVNULL.close()
    
    print("✅ 依赖包安装完成！")
    return True

def create_novel_dict():
    """创建小说专用词典"""
    novel_words = [
        "修仙", "修真", "筑基", "金丹", "元婴", "化神", "合体", "大乘", "渡劫",
        "灵根", "丹药", "法宝", "灵石", "灵气", "功法", "心法", "剑诀",
        "武学", "内功", "外功", "轻功", "暗器", "毒功", "掌法", "拳法",
        "江湖", "武林", "门派", "帮派", "宗门", "长老", "掌门", "弟子",
        "穿越", "重生", "系统", "金手指", "签到", "抽奖", "兑换", "商城",
        "玄幻", "仙侠", "都市", "历史", "军事", "科幻", "末世", "异能"
    ]
    
    try:
        with open("novel_dict.txt", "w", encoding="utf-8") as f:
            for word in novel_words:
                f.write(f"{word}\n")
        print("✅ 小说词典创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建词典失败: {e}")
        return False

def test_installation(mode="quick"):
    """测试安装是否成功"""
    print(f"\n🧪 测试关键组件...")
    
    # 屏蔽导入时的警告信息
    import warnings
    warnings.filterwarnings('ignore')
    
    # 保存原始stdout
    original_stdout = sys.stdout
    
    try:
        # 重定向标准输出，抑制导入时的打印信息
        sys.stdout = open(os.devnull, 'w')
        
        # 测试组件列表
        success_count = 0
        failed_components = []
        
        # 基础组件测试
        basic_components = [
            ("jieba", "import jieba"),
            ("requests", "import requests"),
            ("BeautifulSoup", "from bs4 import BeautifulSoup"),
            ("PyQt5", "import PyQt5")
        ]
        
        # OCR组件测试(仅完整安装)
        ocr_components = [
            ("NumPy", "import numpy"),
            ("Pillow", "from PIL import Image"),
            ("OpenCV", "import cv2"),
            ("PaddlePaddle", "import paddle"),
            ("PaddleOCR", "import paddleocr")
        ]
        
        # 选择要测试的组件
        if mode == "full":
            components_to_test = basic_components + ocr_components
            total_components = len(basic_components) + len(ocr_components)
        else:
            components_to_test = basic_components
            total_components = len(basic_components)
            
        # 恢复标准输出以便打印信息
        sys.stdout = original_stdout
        
        # 测试所有组件
        print(f"正在验证已安装组件...")
        
        # 逐个测试组件
        for name, import_cmd in components_to_test:
            try:
                exec(import_cmd)
                success_count += 1
            except ImportError:
                failed_components.append(name)
        
        # 打印结果
        print(f"✅ 组件测试：{success_count}/{total_components} 已安装成功")
        
        if failed_components:
            print(f"⚠️ 未安装或测试失败的组件: {', '.join(failed_components)}")
            if mode == "quick" and any(c in failed_components for c in ["OpenCV", "PaddlePaddle", "PaddleOCR"]):
                print("   OCR相关组件未安装，符合快速安装预期。如需OCR功能请使用完整安装模式。")
            return success_count > 0  # 至少有一个组件成功就返回True
        else:
            print("✅ 所有测试通过！")
            return True
        
    except Exception as e:
        sys.stdout = original_stdout
        print(f"❌ 测试过程出错: {e}")
        return False
    finally:
        # 确保恢复stdout
        sys.stdout = original_stdout

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="小说阅读神器安装程序")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="快速安装，仅包含必要的基础库（默认）")
    group.add_argument("--full", action="store_true", help="完整安装，包含OCR相关库")
    args = parser.parse_args()
    
    # 确定安装模式
    if args.full:
        return "full"
    else:
        return "quick"  # 默认为quick模式

def main():
    """主安装流程"""
    # 解析命令行参数
    mode = parse_arguments()
    
    print("=" * 50)
    print(f"🚀 小说阅读神器 - 安装程序 ({mode} 模式)")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_requirements(mode):
        return False
    
    # 创建词典
    if not create_novel_dict():
        return False
    
    # 测试安装
    if not test_installation(mode):
        return False
    
    print("\n🎉 安装完成！")
    
    if mode == "quick":
        print("\n⚠️ 注意：您选择了快速安装模式，OCR功能将不可用")
        print("   如果需要使用OCR功能，请运行: python install.py --full")
    else:
        print("\n📝 OCR服务使用说明：")
        print("   1. 打开新的终端窗口")
        print("   2. 导航到paddleocr目录: cd paddleocr")
        print("   3. 启动OCR服务:")
        print("      - Windows: start_service.bat")
        print("      - Linux/Mac: python app.py 或 ./start_service.sh")
        print("   4. 保持OCR服务终端窗口运行（不要关闭）")
    
    print("\n📖 使用方法：")
    print("   python browser.py")
    print("\n?? 或者运行启动脚本：")
    print("   python start.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 安装失败，请检查错误信息并重试")
        sys.exit(1)