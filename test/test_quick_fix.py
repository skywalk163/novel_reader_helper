#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试AI配置修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """快速测试"""
    print("🔧 快速测试AI配置修复")
    
    try:
        # 测试_can_test_connection方法
        from ui.ai_config_dialog import ModelDetailWidget
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        widget = ModelDetailWidget()
        result = widget._can_test_connection()
        print(f"🔧 DEBUG: _can_test_connection()返回: {result} (类型: {type(result)})")
        
        if isinstance(result, bool):
            print("✅ _can_test_connection()返回了正确的布尔值")
            return True
        else:
            print(f"❌ _can_test_connection()返回了错误的类型: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("🎉 AI配置修复验证成功！")
    else:
        print("⚠️ AI配置修复验证失败！")
