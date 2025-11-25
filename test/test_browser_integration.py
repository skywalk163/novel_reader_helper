#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器集成测试脚本
用于验证浏览器模块的初始化和基本功能
"""

import sys
import traceback

def test_browser_import():
    """测试浏览器模块导入"""
    print("=" * 60)
    print("测试1: 浏览器模块导入")
    print("=" * 60)
    
    try:
        from browser import create_browser_window, PYQT_AVAILABLE, get_qapplication
        print("✅ 浏览器模块导入成功")
        print(f"   PyQt5可用性: {PYQT_AVAILABLE}")
        return True
    except Exception as e:
        print(f"❌ 浏览器模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_qapplication_creation():
    """测试QApplication创建"""
    print("\n" + "=" * 60)
    print("测试2: QApplication创建")
    print("=" * 60)
    
    try:
        from browser import get_qapplication, PYQT_AVAILABLE
        
        if not PYQT_AVAILABLE:
            print("⚠️  PyQt5不可用，跳过测试")
            return False
            
        app = get_qapplication()
        print(f"✅ QApplication创建成功: {app}")
        return True
    except Exception as e:
        print(f"❌ QApplication创建失败: {e}")
        traceback.print_exc()
        return False

def test_browser_window_creation():
    """测试浏览器窗口创建"""
    print("\n" + "=" * 60)
    print("测试3: 浏览器窗口创建")
    print("=" * 60)
    
    try:
        from browser import create_browser_window, PYQT_AVAILABLE
        
        if not PYQT_AVAILABLE:
            print("⚠️  PyQt5不可用，跳过测试")
            return False
            
        browser = create_browser_window(None)
        print(f"✅ 浏览器窗口创建成功")
        
        # 检查关键属性
        if hasattr(browser, 'web_view'):
            print("   ✅ web_view属性存在")
        else:
            print("   ❌ web_view属性缺失")
            return False
            
        if hasattr(browser, 'web_page'):
            print("   ✅ web_page属性存在")
        else:
            print("   ❌ web_page属性缺失")
            return False
            
        if hasattr(browser, 'address_bar'):
            print("   ✅ address_bar属性存在")
        else:
            print("   ❌ address_bar属性缺失")
            return False
            
        # 测试信号连接
        try:
            if hasattr(browser, 'page_loaded'):
                print("   ✅ page_loaded信号存在")
            if hasattr(browser, 'content_extracted'):
                print("   ✅ content_extracted信号存在")
        except Exception as e:
            print(f"   ⚠️  信号检查时出现警告: {e}")
        
        # 清理
        browser.close()
        print("   ✅ 浏览器窗口关闭成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器窗口创建失败: {e}")
        traceback.print_exc()
        return False

def test_browser_basic_operations():
    """测试浏览器基本操作"""
    print("\n" + "=" * 60)
    print("测试4: 浏览器基本操作")
    print("=" * 60)
    
    try:
        from browser import create_browser_window, PYQT_AVAILABLE
        
        if not PYQT_AVAILABLE:
            print("⚠️  PyQt5不可用，跳过测试")
            return False
            
        browser = create_browser_window(None)
        
        # 测试URL加载
        test_url = "https://www.baidu.com"
        print(f"   测试加载URL: {test_url}")
        browser.load_url(test_url)
        print("   ✅ URL加载命令执行成功")
        
        # 测试获取当前URL
        current_url = browser.get_current_url()
        print(f"   当前URL: {current_url}")
        
        # 清理
        browser.close()
        print("   ✅ 测试完成，浏览器已关闭")
        
        return True
        
    except Exception as e:
        print(f"❌ 浏览器基本操作测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("浏览器集成测试开始")
    print("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_browser_import()))
    results.append(("QApplication创建", test_qapplication_creation()))
    results.append(("浏览器窗口创建", test_browser_window_creation()))
    results.append(("基本操作", test_browser_basic_operations()))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            status = "✅ 通过"
            passed += 1
        elif result is False:
            status = "❌ 失败"
            failed += 1
        else:
            status = "⚠️  跳过"
            skipped += 1
        print(f"{test_name:20s}: {status}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    print("=" * 60 + "\n")
    
    if failed == 0:
        print("🎉 所有测试通过！浏览器模块工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())