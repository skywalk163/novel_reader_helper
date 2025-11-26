#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OCR 图片识别功能
"""

import urllib.request
import urllib.parse
import json
import os
import time

OCR_SERVICE_URL = "http://127.0.0.1:5000"

def test_ocr_image(image_path):
    start_time = time.time()
    """测试OCR图片识别"""
    print("=" * 60)
    print("OCR 图片识别测试")
    print("=" * 60)
    print(f"图片路径: {image_path}")
    print(f"服务地址: {OCR_SERVICE_URL}")
    print("-" * 60)
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    print("✅ 图片文件存在")
    print(f"   文件大小: {os.path.getsize(image_path)} 字节")
    
    # 调用OCR服务
    try:
        url = f"{OCR_SERVICE_URL}/ocr/local"
        params = {"path": image_path}
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        
        print(f"\n正在调用OCR服务...")
        print(f"请求URL: {full_url}")
        
        request = urllib.request.Request(full_url, method="GET")
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
        
        print("\n" + "=" * 60)
        print("OCR 识别结果")
        print("=" * 60)
        print(f"原始响应: {result}")
        print("-" * 60)
        
        if result.get("success", False):
            data = result.get("data", [])
            print(f"✅ 识别成功，共识别出 {len(data)} 行文字\n")
            
            # 显示识别的文字
            for i, item in enumerate(data, 1):
                text = item.get("text", "")
                confidence = item.get("confidence", 0)
                print(f"{i}. {text}")
                print(f"   置信度: {confidence:.2%}\n")
            
            # 组合完整文本
            full_text = "\n".join([item["text"] for item in data])
            print("\n" + "-" * 60)
            print("完整文本内容:")
            print("-" * 60)
            print(full_text)
            
            # 保存结果
            output_file = image_path.replace(".png", "_ocr_result.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"\n✅ 识别结果已保存到: {output_file}")
            
        else:
            message = result.get("message", "未知错误")
            error = result.get("error", "")
            print(f"❌ OCR识别失败: {message}")
            if error:
                print(f"   错误详情: {error}")
            
    except Exception as e:
        print(f"\n❌ OCR过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print(f"总耗时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    # 测试图片路径
    image_path = r"E:\comatework\novel_reader_helper\test\ocrtest.png"
    test_ocr_image(image_path)