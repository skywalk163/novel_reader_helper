#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR 服务测试脚本
测试 OCR 服务是否正常运行
"""

import requests
import os
import sys
import json

def test_service_status():
    """测试服务状态"""
    try:
        response = requests.get("http://127.0.0.1:5000/status")
        if response.status_code == 200:
            print("✅ OCR 服务运行正常")
            return True
        else:
            print(f"❌ OCR 服务响应异常，状态码：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ OCR 服务未启动或无法连接")
        return False

def test_ocr_with_sample_image():
    """使用样例图片测试 OCR 功能"""
    # 寻找测试图片
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image = None
    
    # 检查当前目录
    for file in os.listdir(current_dir):
        if file.endswith(('.jpg', '.png', '.jpeg', '.bmp')):
            test_image = os.path.join(current_dir, file)
            break
    
    # 如果没有找到图片，检查上级目录的 test 文件夹
    if not test_image:
        parent_dir = os.path.dirname(current_dir)
        test_dir = os.path.join(parent_dir, "test")
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.endswith(('.jpg', '.png', '.jpeg', '.bmp')):
                    test_image = os.path.join(test_dir, file)
                    break
    
    if not test_image:
        print("❌ 未找到测试图片，无法测试 OCR 功能")
        return False
    
    # 上传图片进行 OCR 测试
    try:
        with open(test_image, 'rb') as f:
            print(f"正在使用测试图片：{test_image}")
            files = {'file': f}
            response = requests.post("http://127.0.0.1:5000/ocr", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ OCR 测试成功！识别结果：")
                for idx, item in enumerate(result.get('results', [])):
                    print(f"  {idx + 1}. {item['text']} (置信度: {item['confidence']:.2f})")
                return True
            else:
                print(f"❌ OCR 处理失败：{result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ OCR 请求失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OCR 测试异常：{e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PaddleOCR 服务测试")
    print("=" * 50)
    
    # 测试服务状态
    if not test_service_status():
        print("\n请确保 OCR 服务已经启动：")
        print("  1. 在另一个终端窗口运行：python app.py")
        print("  2. 或者运行启动脚本：start_service.bat (Windows) / start_service.sh (Linux/Mac)")
        sys.exit(1)
    
    # 测试 OCR 功能
    print("\n测试 OCR 功能...")
    test_ocr_with_sample_image()