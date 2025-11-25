#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PyQt5和PyQtWebEngine导入
"""

print("开始测试PyQt5导入...")

try:
    from PyQt5.QtCore import QUrl, pyqtSignal, QTimer
    print("✅ PyQt5.QtCore 导入成功")
except ImportError as e:
    print(f"❌ PyQt5.QtCore 导入失败: {e}")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    print("✅ PyQt5.QtWidgets 导入成功")
except ImportError as e:
    print(f"❌ PyQt5.QtWidgets 导入失败: {e}")

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
    print("✅ PyQt5.QtWebEngineWidgets 导入成功")
except ImportError as e:
    print(f"❌ PyQt5.QtWebEngineWidgets 导入失败: {e}")

try:
    from PyQt5.QtGui import QIcon, QKeySequence
    print("✅ PyQt5.QtGui 导入成功")
except ImportError as e:
    print(f"❌ PyQt5.QtGui 导入失败: {e}")

print("\n开始测试browser.py模块导入...")

try:
    from browser import create_browser_window, PYQT_AVAILABLE
    print(f"✅ browser模块导入成功")
    print(f"   PYQT_AVAILABLE = {PYQT_AVAILABLE}")
    
    if PYQT_AVAILABLE:
        print("\n?? 所有依赖检查通过！浏览器功能可用！")
    else:
        print("\n⚠️ PyQt5依赖不完整，浏览器功能不可用")
        
except ImportError as e:
    print(f"❌ browser模块导入失败: {e}")

print("\n测试完成！")