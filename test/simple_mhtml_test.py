#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的MHTML文件内容提取测试
专注于直接解析，避免浏览器渲染的复杂性
"""

import os
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote

def analyze_mhtml_structure(file_path):
    """分析MHTML文件结构"""
    print("=== MHTML文件结构分析 ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        print(f"文件总长度: {len(content)} 字符")
        
        # 寻找HTML内容
        html_matches = list(re.finditer(r'<html[\s\S]*?</html>', content, re.IGNORECASE))
        print(f"找到 {len(html_matches)} 个HTML块")
        
        # 寻找可能的小说内容标识
        novel_patterns = [
            r'class="read-content"',
            r'class="j_readContent"',
            r'class="chapter"',
            r'id="content"',
            r'<h1[^>]*>.*?章.*?</h1>',
            r'<div[^>]*content[^>]*>'
        ]
        
        for pattern in novel_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"找到模式 '{pattern}': {len(matches)} 次")
        
        return content
        
    except Exception as e:
        print(f"分析文件时出错: {e}")
        return None

def extract_from_mhtml_advanced(file_path):
    """高级MHTML内容提取"""
    print("\n=== 高级MHTML内容提取 ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            mhtml_content = file.read()
        
        # 寻找所有HTML块
        html_blocks = re.findall(r'<html[\s\S]*?</html>', mhtml_content, re.IGNORECASE)
        print(f"找到 {len(html_blocks)} 个HTML块")
        
        results = []
        
        for i, html_block in enumerate(html_blocks):
            print(f"\n--- 处理HTML块 {i+1} ---")
            
            soup = BeautifulSoup(html_block, 'html.parser')
            
            # 查找标题 - 使用多种选择器
            title_selectors = [
                'h1.j_chapterName',
                'h1[class*="chapter"]',
                '.chapter-title',
                'h1',
                'h2',
                '.title'
            ]
            
            title = "未找到标题"
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()
                    print(f"使用选择器 '{selector}' 找到标题")
                    break
            
            # 查找内容 - 使用多种选择器
            content_selectors = [
                '.read-content',
                '.j_readContent',
                '[class*="read-content"]',
                '[class*="chapter-content"]',
                '[id*="content"]',
                '.content',
                'main',
                'article'
            ]
            
            content = "未找到正文内容"
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 尝试提取所有段落
                    paragraphs = content_elem.find_all(['p', 'div'])
                    if paragraphs:
                        content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    else:
                        content = content_elem.get_text().strip()
                    
                    if len(content) > 100:  # 只接受足够长的内容
                        print(f"使用选择器 '{selector}' 找到内容")
                        break
            
            # 处理可能的编码问题
            if title and title != "未找到标题":
                # 尝试URL解码
                try:
                    decoded_title = unquote(title)
                    if decoded_title != title:
                        title = decoded_title
                        print("标题经过URL解码")
                except:
                    pass
            
            result = {
                'block_index': i + 1,
                'title': title,
                'content': content,
                'content_length': len(content)
            }
            
            results.append(result)
            
            print(f"标题: {title}")
            print(f"内容长度: {len(content)}")
            if len(content) > 50:
                print(f"内容预览: {content[:200]}...")
        
        return results
        
    except Exception as e:
        print(f"提取内容时出错: {e}")
        return []

def test_current_browser_integration(results):
    """测试与当前浏览器集成的兼容性"""
    print("\n=== 浏览器集成兼容性测试 ===")
    
    if not results:
        print("没有提取结果可供测试")
        return
    
    # 找到最佳结果（内容最长的）
    best_result = max(results, key=lambda x: x['content_length'])
    
    print(f"最佳提取结果来自HTML块 {best_result['block_index']}")
    print(f"标题: {best_result['title']}")
    print(f"内容长度: {best_result['content_length']} 字符")
    
    if best_result['content_length'] > 100:
        print("✅ 提取成功！这个结果可以用于浏览器集成")
        
        # 模拟浏览器提取结果格式
        browser_compatible_result = {
            'title': best_result['title'],
            'text': best_result['content'],
            'word_count': best_result['content_length'],
            'images': [],  # MHTML文件中的图片需要特殊处理
            'chapter_info': {
                'source': 'MHTML文件',
                'extraction_method': 'direct_parsing'
            }
        }
        
        print("浏览器兼容格式:")
        print(f"  标题: {browser_compatible_result['title']}")
        print(f"  字数: {browser_compatible_result['word_count']}")
        print(f"  内容预览: {browser_compatible_result['text'][:100]}...")
        
        return browser_compatible_result
    else:
        print("❌ 提取失败，内容太短或为空")
        return None

def main():
    """主测试函数"""
    file_path = r"E:\360Downloads\test.mhtml"
    
    print("🎯 简化MHTML文件内容提取测试")
    print(f"目标文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件 {file_path} 不存在")
        return
    
    # 1. 分析文件结构
    mhtml_content = analyze_mhtml_structure(file_path)
    if not mhtml_content:
        return
    
    # 2. 高级内容提取
    results = extract_from_mhtml_advanced(file_path)
    
    # 3. 浏览器集成测试
    compatible_result = test_current_browser_integration(results)
    
    # 4. 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    if compatible_result:
        print("✅ 测试成功！")
        print("可以将这种提取方法集成到现有的小说阅读器中")
        print("\n建议的集成步骤:")
        print("1. 在browser.py中添加MHTML文件检测")
        print("2. 当检测到本地MHTML文件时，使用直接解析方法")
        print("3. 跳过JavaScript执行，直接返回解析结果")
    else:
        print("❌ 测试失败")
        print("需要进一步分析MHTML文件格式或尝试其他提取方法")

if __name__ == "__main__":
    main()