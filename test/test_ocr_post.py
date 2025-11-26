#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OCR 图片识别功能 - 使用POST方法
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import os
import time
import mimetypes
from urllib.parse import urljoin
import uuid

OCR_SERVICE_URL = "http://127.0.0.1:5000"

def test_ocr_post(image_path):
    """使用POST方法测试OCR图片识别"""
    start_time = time.time()
    print("=" * 60)
    print("OCR 图片识别测试 (POST方法)")
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
    
    # 准备POST请求
    try:
        # 生成唯一边界标识符
        boundary = str(uuid.uuid4())
        
        # 设置Content-Type
        content_type = f'multipart/form-data; boundary={boundary}'
        
        # 构建multipart/form-data请求体
        body = []
        # 添加文件数据
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(image_path)}"'.encode())
        
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type:
            body.append(f'Content-Type: {mime_type}'.encode())
        body.append(b'')
        
        # 读取并添加文件内容
        with open(image_path, 'rb') as f:
            body.append(f.read())
        
        # 添加结束边界
        body.append(f'--{boundary}--'.encode())
        body.append(b'')
        
        # 将请求体连接成一个字节串，使用CRLF作为分隔符
        data = b'\r\n'.join(body)
        
        # 创建请求
        url = urljoin(OCR_SERVICE_URL, "/ocr")
        print(f"\n正在调用OCR服务...")
        print(f"请求URL: {url}")
        print(f"请求方法: POST")
        
        request = urllib.request.Request(url, data=data, method="POST")
        request.add_header('Content-Type', content_type)
        request.add_header('Content-Length', str(len(data)))
        
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
        
        print("\n" + "=" * 60)
        print("OCR 识别结果")
        print("=" * 60)
        
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
            output_file = image_path.replace(".png", "_ocr_result.txt").replace(".jpg", "_ocr_result.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"\n✅ 识别结果已保存到: {output_file}")
            
        else:
            message = result.get("message", "未知错误")
            error = result.get("error", "")
            print(f"❌ OCR识别失败: {message}")
            if error:
                print(f"   错误详情: {error}")
            print(f"   完整响应: {result}")
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP错误: {e.code} - {e.reason}")
        try:
            error_content = e.read().decode()
            print(f"   错误响应内容: {error_content}")
        except:
            pass
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
    test_ocr_post(image_path)