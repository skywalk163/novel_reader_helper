#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OCR 服务连接
"""

import urllib.request
import urllib.parse
import json

OCR_SERVICE_URL = "http://127.0.0.1:5000"

def test_ocr_service():
    """测试OCR服务"""
    print("正在测试 OCR 服务连接...")
    print(f"服务地址: {OCR_SERVICE_URL}")
    print("-" * 50)
    
    # 测试1: 检查服务是否运行
    try:
        response = urllib.request.urlopen(f"{OCR_SERVICE_URL}/status", timeout=2)
        print(f"✅ 服务状态检查成功，状态码: {response.status}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"⚠️  状态端点不存在 (404)，但服务可能仍在运行")
            print("   尝试其他端点...")
        else:
            print(f"❌ 服务状态检查失败: HTTP {e.code}")
    except Exception as e:
        print(f"❌ 无法连接到服务: {str(e)}")
        print("   请确保 PaddleOCR 服务正在运行")
        return False
    
    # 测试2: 列出可用的 API 端点
    print("\n可用的 OCR API 端点:")
    print("1. GET  /ocr/local?path=图片路径")
    print("2. POST /ocr (上传文件)")
    print("3. GET  /ocr?url=图片URL")
    
    print("\n" + "=" * 50)
    print("OCR 服务测试完成")
    return True

if __name__ == "__main__":
    test_ocr_service()