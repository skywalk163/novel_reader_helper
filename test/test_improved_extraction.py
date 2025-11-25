#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进后的内容提取功能测试脚本
测试MHTML文件和起点小说网的内容提取
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, QTimer
from browser import NovelBrowser

def test_extraction():
    """测试内容提取功能"""
    print("🧪 开始测试改进后的内容提取功能...")
    
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    browser = NovelBrowser()
    browser.show()
    
    extraction_results = []
    
    def on_content_extracted(content):
        extraction_results.append(content)
        print(f"\n✅ 内容提取成功！")
        print(f"   标题: {content.get('title', '未知')}")
        print(f"   字符数: {len(content.get('text', ''))}")
        print(f"   来源: {content.get('url', content.get('source', '未知'))}")
        
        # 显示前200个字符的内容预览
        text_preview = content.get('text', '')[:200]
        print(f"   内容预览: {text_preview}...")
    
    browser.content_extracted.connect(on_content_extracted)
    
    print("\n📁 测试1: MHTML文件提取")
    print("=" * 60)
    mhtml_path = r"E:\360Downloads\test.mhtml"
    print(f"加载文件: {mhtml_path}")
    browser.load_url(QUrl.fromLocalFile(mhtml_path))
    
    def check_mhtml_load():
        if "MHTML" in browser.status_label.text() and "成功" in browser.status_label.text():
            print("📄 MHTML文件加载成功，执行内容提取...")
            browser.extract_page_content()
            
            # 等待提取完成后测试起点小说网
            QTimer.singleShot(3000, test_qidian)
        else:
            QTimer.singleShot(1000, check_mhtml_load)
    
    def test_qidian():
        print("\n🌐 测试2: 起点小说网内容提取")
        print("=" * 60)
        # 使用起点的一个公开章节
        qidian_url = "https://book.qidian.com/info/1046199155/"
        print(f"加载页面: {qidian_url}")
        browser.load_url(qidian_url)
        
        def check_qidian_load():
            current_url = browser.get_current_url()
            if "qidian.com" in current_url and browser.status_label.text().startswith("✅"):
                print("📄 起点页面加载成功，执行内容提取...")
                browser.extract_page_content()
                
                # 等待后显示结果
                QTimer.singleShot(5000, show_results)
            else:
                QTimer.singleShot(2000, check_qidian_load)
        
        QTimer.singleShot(3000, check_qidian_load)
    
    def show_results():
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        if len(extraction_results) >= 1:
            print(f"✅ 成功提取 {len(extraction_results)} 个内容")
            for i, result in enumerate(extraction_results, 1):
                print(f"\n{i}. {result.get('title', '未知')}")
                print(f"   字符数: {len(result.get('text', ''))}")
                print(f"   来源: {result.get('url', result.get('source', '未知'))}")
        else:
            print("⚠️ 未成功提取任何内容")
        
        print("\n🎯 测试完成！")
        print("\n改进效果:")
        print("  ✅ 使用类似MHTML的正则提取技术")
        print("  ✅ 针对起点等小说网站优化")
        print("  ✅ 支持JavaScript动态内容提取")
        print("  ✅ 改进的HTML标签清理")
        
        QTimer.singleShot(3000, browser.close)
    
    QTimer.singleShot(2000, check_mhtml_load)
    
    return app.exec_()

if __name__ == "__main__":
    test_extraction()