#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浏览器内容提取功能
"""

import sys
import time

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    from browser import create_browser_window
    
    def test_browser_extract():
        """测试浏览器内容提取"""
        print("=" * 60)
        print("开始测试浏览器内容提取功能")
        print("=" * 60)
        
        app = QApplication(sys.argv)
        
        # 创建浏览器窗口
        print("\n1. 创建浏览器窗口...")
        browser = create_browser_window(None)
        
        # 检查关键组件
        print("\n2. 检查关键组件...")
        checks = {
            "web_view": hasattr(browser, 'web_view') and browser.web_view is not None,
            "extract_content_action": hasattr(browser, 'extract_content_action') and browser.extract_content_action is not None,
            "web_extractor": hasattr(browser, 'web_extractor') and browser.web_extractor is not None,
        }
        
        for name, result in checks.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {name}: {status}")
        
        if not all(checks.values()):
            print("\n❌ 组件检查失败，请检查browser.py初始化代码")
            return False
        
        print("\n3. 测试内容提取信号...")
        content_received = [False]
        
        def on_content_extracted(content):
            print(f"   ✅ 收到提取内容信号")
            print(f"   内容长度: {len(content.get('text', ''))}")
            content_received[0] = True
            QTimer.singleShot(1000, app.quit)
        
        browser.content_extracted.connect(on_content_extracted)
        
        # 加载测试页面
        print("\n4. 加载测试页面...")
        test_url = "https://www.qidian.com"
        browser.load_url(test_url)
        browser.show()
        
        # 等待页面加载后提取内容
        def try_extract():
            print("\n5. 尝试提取页面内容...")
            try:
                browser.extract_page_content()
                print("   ✅ 提取命令已发送")
            except Exception as e:
                print(f"   ❌ 提取失败: {e}")
                app.quit()
        
        # 页面加载完成后3秒提取
        QTimer.singleShot(5000, try_extract)
        
        # 15秒超时
        QTimer.singleShot(15000, app.quit)
        
        print("\n等待测试完成（最多15秒）...")
        app.exec_()
        
        print("\n" + "=" * 60)
        if content_received[0]:
            print("✅ 测试通过！浏览器内容提取功能正常")
        else:
            print("⚠️ 测试未完成，可能需要更长时间或网络问题")
        print("=" * 60)
        
        return content_received[0]
    
    if __name__ == "__main__":
        try:
            success = test_browser_extract()
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"\n❌ 测试过程出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保已安装必要的依赖:")
    print("pip install PyQt5 PyQtWebEngine")
    sys.exit(1)