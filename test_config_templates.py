#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模板测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_templates():
    """测试配置模板功能"""
    try:
        # 测试导入config模块
        import config
        print("✅ 成功导入config模块")
        
        # 检查AI_TEMPLATES是否存在
        if hasattr(config, 'AI_TEMPLATES'):
            print("✅ AI_TEMPLATES属性存在")
            
            templates = config.AI_TEMPLATES
            print(f"✅ 模板数量: {len(templates)}")
            
            # 验证常用模板
            expected_templates = ['openai', 'azure', 'localai', 'ollama']
            for template_name in expected_templates:
                if template_name in templates:
                    template = templates[template_name]
                    print(f"✅ 模板 '{template_name}' 存在: {template.get('name', 'N/A')}")
                    
                    # 检查模板必需字段
                    required_fields = ['name', 'base_url', 'model_name', 'description']
                    for field in required_fields:
                        if field in template:
                            print(f"  ✅ 字段 '{field}': {template[field]}")
                        else:
                            print(f"  ❌ 缺少字段: {field}")
                            return False
                else:
                    print(f"❌ 模板 '{template_name}' 不存在")
                    return False
            
            print("✅ 所有模板验证通过")
            return True
        else:
            print("❌ AI_TEMPLATES属性不存在")
            print(f"config模块属性: {[attr for attr in dir(config) if not attr.startswith('_')]}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入config失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始配置模板测试")
    print("=" * 50)
    
    success = test_config_templates()
    
    print("=" * 50)
    if success:
        print("🎉 配置模板测试成功！")
        sys.exit(0)
    else:
        print("❌ 配置模板测试失败！")
        sys.exit(1)
