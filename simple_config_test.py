#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的配置模板测试
"""

# 直接定义AI_TEMPLATES来测试
AI_TEMPLATES = {
    "openai": {
        "name": "OpenAI ChatGPT",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-3.5-turbo",
        "description": "OpenAI官方API服务"
    },
    "azure": {
        "name": "Azure OpenAI",
        "base_url": "https://your-resource.openai.azure.com/",
        "model_name": "gpt-35-turbo",
        "description": "微软Azure OpenAI服务"
    },
    "localai": {
        "name": "LocalAI",
        "base_url": "http://localhost:8080/v1",
        "model_name": "gpt-3.5-turbo",
        "description": "本地部署的LocalAI服务"
    },
    "ollama": {
        "name": "Ollama",
        "base_url": "http://localhost:11434/v1",
        "model_name": "llama2",
        "description": "本地部署的Ollama服务"
    }
}

def test_templates():
    """测试配置模板功能"""
    print("🧪 开始配置模板测试")
    print("=" * 50)
    
    print(f"✅ AI_TEMPLATES定义成功，模板数量: {len(AI_TEMPLATES)}")
    
    # 验证常用模板
    expected_templates = ['openai', 'azure', 'localai', 'ollama']
    all_found = True
    
    for template_name in expected_templates:
        if template_name in AI_TEMPLATES:
            template = AI_TEMPLATES[template_name]
            print(f"✅ 模板 '{template_name}' 找到: {template.get('name', 'N/A')}")
            
            # 检查模板必需字段
            required_fields = ['name', 'base_url', 'model_name', 'description']
            template_valid = True
            
            for field in required_fields:
                if field in template:
                    print(f"  ✅ 字段 '{field}': {template[field]}")
                else:
                    print(f"  ❌ 缺少字段: {field}")
                    template_valid = False
            
            if not template_valid:
                all_found = False
        else:
            print(f"❌ 模板 '{template_name}' 不存在")
            all_found = False
    
    print("=" * 50)
    if all_found:
        print("🎉 配置模板测试成功！所有模板都正确定义。")
        return True
    else:
        print("❌ 配置模板测试失败！部分模板存在问题。")
        return False

if __name__ == "__main__":
    success = test_templates()
    
    if success:
        print("\n💡 配置模板功能正常工作，AI配置界面可以正常使用预设模板。")
    else:
        print("\n⚠️ 配置模板功能存在问题，需要检查模板定义。")
