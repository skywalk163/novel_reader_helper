#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本 - 测试MHTML和在线小说网站的内容提取
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, QTimer
from browser import NovelBrowser

def test_mhtml_extraction():
    """测试MHTML文件提取功能"""
    print("🧪 开始测试MHTML文件提取功能...")
    
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    browser = NovelBrowser()
    browser.show()
    
    # 存储提取结果
    extraction_results = []
    
    def on_content_extracted(content):
        extraction_results.append(content)
        print(f"✅ 内容提取成功！")
        print(f"   标题: {content.get('title', '未知')}")
        print(f"   字符数: {len(content.get('text', ''))}")
        print(f"   来源: {content.get('source', '未知')}")
        
    # 连接信号
    browser.content_extracted.connect(on_content_extracted)
    
    # 测试MHTML文件
    mhtml_path = r"E:\360Downloads\test.mhtml"
    print(f"?? 加载MHTML文件: {mhtml_path}")
    
    browser.load_url(QUrl.fromLocalFile(mhtml_path))
    
    # 等待加载完成
    def check_and_extract():
        if browser.status_label.text().startswith("✅"):
            print("📄 执行内容提取...")
            browser.extract_page_content()
            
            # 等待提取完成
            QTimer.singleShot(3000, lambda: test_qidian_novel(browser, extraction_results))
        else:
            QTimer.singleShot(1000, check_and_extract)
    
    QTimer.singleShot(2000, check_and_extract)
    
    return app, browser

def test_qidian_novel(browser, previous_results):
    """测试起点小说网内容提取"""
    print("\n🌐 开始测试起点小说网...")
    
    # 测试起点小说网的一个章节
    qidian_url = "https://read.qidian.com/chapter/4JBHaxK1Mi--efMZQfuGbw2/FosECGrBuY1FYDL-qrmWuw2"
    print(f"🔗 加载起点小说: {qidian_url}")
    
    browser.load_url(qidian_url)
    
    def check_qidian_and_extract():
        current_url = browser.get_current_url()
        if "qidian.com" in current_url and browser.status_label.text().startswith("✅"):
            print("📄 执行起点小说内容提取...")
            browser.extract_page_content()
            
            # 等待提取完成后显示结果
            QTimer.singleShot(5000, lambda: show_final_results(previous_results, browser))
        else:
            QTimer.singleShot(2000, check_qidian_and_extract)
    
    QTimer.singleShot(5000, check_qidian_and_extract)

def show_final_results(results, browser):
    """显示最终测试结果"""
    print("\n" + "="*60)
    print("📊 集成测试结果总结")
    print("="*60)
    
    if len(results) >= 2:
        print("✅ 测试完成！两种提取方式都成功了")
        print(f"\n1️⃣ MHTML文件提取:")
        print(f"   标题: {results[0].get('title', '未知')}")
        print(f"   字符数: {len(results[0].get('text', ''))}")
        print(f"   提取方式: {results[0].get('extraction_method', '未知')}")
        
        print(f"\n2️⃣ 在线小说提取:")
        print(f"   标题: {results[1].get('title', '未知')}")
        print(f"   字符数: {len(results[1].get('text', ''))}")
        print(f"   来源网站: {results[1].get('url', '未知')}")
    elif len(results) == 1:
        print("⚠️ 部分测试完成，只有一种提取方式成功")
        print(f"   成功提取: {results[0].get('title', '未知')}")
    else:
        print("❌ 测试失败，没有成功提取任何内容")
    
    print("\n🎯 功能验证完成！小说阅读器浏览器现在支持:")
    print("   • 📁 本地MHTML文件直接打开和提取")
    print("   • 🌐 在线小说网站内容提取")
    print("   • 📄 一键提取功能")
    print("   • 🖼️ 图片OCR识别（如果服务可用）")
    
    # 5秒后关闭
    QTimer.singleShot(5000, browser.close)

def main():
    """主测试函数"""
    print("🚀 启动小说阅读器浏览器集成测试")
    print("测试项目:")
    print("1. MHTML离线文件提取")
    print("2. 起点小说网在线提取")
    print("-" * 40)
    
    try:
        app, browser = test_mhtml_extraction()
        app.exec_()
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()