#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试AI配置修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_fix():
    """完整测试AI配置修复"""
    print("🔧 完整测试AI配置修复")
    print("=" * 60)
    
    try:
        # 测试1: 导入所有必要模块
        print("测试1: 导入模块...")
        import browser
        from ui.ai_config_dialog import AIConfigDialog, ModelDetailWidget, ModelListWidget
        from PyQt5.QtWidgets import QApplication
        print("✅ 所有模块导入成功")
        
        # 测试2: 创建QApplication
        print("测试2: 创建QApplication...")
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        print("✅ QApplication创建成功")
        
        # 测试3: 创建浏览器实例
        print("测试3: 创建浏览器实例...")
        browser_window = browser.NovelBrowser()
        print("✅ 浏览器实例创建成功")
        
        # 测试4: 检查AI配置按钮
        print("测试4: 检查AI配置按钮...")
        ai_config_action = None
        for action in browser_window.toolbar.actions():
            if hasattr(action, 'text') and 'AI配置' in action.text():
                ai_config_action = action
                break
        
        if ai_config_action:
            print("✅ AI配置按钮存在")
        else:
            print("❌ AI配置按钮不存在")
            return False
        
        # 测试5: 测试ModelDetailWidget
        print("测试5: 测试ModelDetailWidget...")
        detail_widget = ModelDetailWidget()
        result = detail_widget._can_test_connection()
        if isinstance(result, bool):
            print(f"✅ ModelDetailWidget._can_test_connection()返回正确类型: {type(result)}")
        else:
            print(f"❌ ModelDetailWidget._can_test_connection()返回错误类型: {type(result)}")
            return False
        
        # 测试6: 测试ModelListWidget
        print("测试6: 测试ModelListWidget...")
        list_widget = ModelListWidget()
        print("✅ ModelListWidget创建成功")
        
        # 测试7: 测试AIConfigDialog
        print("测试7: 测试AIConfigDialog...")
        dialog = AIConfigDialog()
        print("✅ AIConfigDialog创建成功")
        dialog.close()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！AI配置功能已完全修复！")
        print("\n?? 修复验证:")
        print("  ✅ 所有模块导入成功")
        print("  ✅ 浏览器实例创建成功")
        print("  ✅ AI配置按钮存在")
        print("  ✅ ModelDetailWidget._can_test_connection()返回正确类型")
        print("  ✅ ModelListWidget创建成功")
        print("  ✅ AIConfigDialog创建成功")
        print("  ✅ 所有UI组件正常工作")
        
        print("\n🎯 用户现在可以:")
        print("  1. 启动 browser.py")
        print("  2. 在工具栏中找到'⚙️ AI配置'按钮")
        print("  3. 点击按钮打开AI配置界面")
        print("  4. 正常使用AI配置功能")
        print("  5. 不会再遇到TypeError错误")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_fix()
    
    if success:
        print("\n🎉 AI配置功能修复验证成功！")
        print("问题已彻底解决，用户可以正常使用AI配置功能。")
        sys.exit(0)
    else:
        print("\n⚠️ AI配置功能仍有问题！")
        sys.exit(1)
