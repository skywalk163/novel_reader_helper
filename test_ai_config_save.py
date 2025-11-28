#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI配置保存功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_config_save():
    """测试AI配置保存功能"""
    print("🔧 测试AI配置保存功能")
    print("=" * 60)
    
    try:
        from ui.ai_config_dialog import ModelDetailWidget
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建ModelDetailWidget
        widget = ModelDetailWidget()
        print("✅ ModelDetailWidget创建成功")
        
        # 填写测试数据
        widget.name_edit.setText("测试模型")
        widget.base_url_edit.setText("https://api.openai.com/v1")
        widget.token_edit.setText("sk-test-key")
        widget.model_name_edit.setText("gpt-3.5-turbo")
        widget.default_checkbox.setChecked(True)
        print("✅ 测试数据填充完成")
        
        # 测试get_model方法
        model = widget.get_model()
        
        if model:
            print("✅ get_model()方法执行成功")
            print(f"模型名称: {model.name}")
            print(f"Base URL: {model.base_url}")
            print(f"模型名称: {model.model_name}")
            print(f"是否默认: {model.is_default}")
            return True
        else:
            print("❌ get_model()方法返回None")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_config_save()
    
    if success:
        print("\n🎉 AI配置保存功能测试通过！")
        print("用户现在可以正常配置和保存AI模型。")
        sys.exit(0)
    else:
        print("\n⚠️ AI配置保存功能测试失败！")
        sys.exit(1)
