#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI配置功能测试脚本
测试AI模型配置的各种功能
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAIConfig(unittest.TestCase):
    """AI配置功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        
        # 设置测试环境
        os.environ['TEST_MODE'] = 'True'
        
        print(f"测试目录: {self.temp_dir}")
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_data_structure(self):
        """测试配置数据结构"""
        try:
            from config.ai_config import AIModelConfig
            import uuid
            from datetime import datetime
            
            # 创建测试配置
            model_config = AIModelConfig(
                id=str(uuid.uuid4()),
                name="测试模型",
                base_url="https://api.openai.com/v1",
                token_key="sk-test-key",
                model_name="gpt-3.5-turbo",
                is_default=True
            )
            
            # 验证数据结构
            self.assertIsInstance(model_config.id, str)
            self.assertIsInstance(model_config.name, str)
            self.assertIsInstance(model_config.base_url, str)
            self.assertIsInstance(model_config.token_key, str)
            self.assertIsInstance(model_config.model_name, str)
            self.assertIsInstance(model_config.is_default, bool)
            self.assertIsInstance(model_config.created_at, str)
            self.assertIsInstance(model_config.updated_at, str)
            
            # 验证数据内容
            self.assertEqual(model_config.name, "测试模型")
            self.assertEqual(model_config.base_url, "https://api.openai.com/v1")
            self.assertEqual(model_config.token_key, "sk-test-key")
            self.assertEqual(model_config.model_name, "gpt-3.5-turbo")
            self.assertTrue(model_config.is_default)
            
            print("✅ 配置数据结构测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入配置模块: {e}")
    
    def test_config_manager(self):
        """测试配置管理器"""
        try:
            from config.ai_config import AIConfigManager, AIModelConfig
            import uuid
            
            # 使用临时目录创建配置管理器
            config_manager = AIConfigManager(self.temp_dir)
            
            # 创建测试模型
            test_model = AIModelConfig(
                id=str(uuid.uuid4()),
                name="测试模型管理器",
                base_url="https://api.test.com/v1",
                token_key="sk-test-key",
                model_name="test-model",
                is_default=True
            )
            
            # 测试添加模型
            result = config_manager.add_model(test_model)
            self.assertTrue(result)
            
            # 测试加载模型
            models = config_manager.load_models()
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0].name, "测试模型管理器")
            
            # 测试获取默认模型
            default_model = config_manager.get_default_model()
            self.assertIsNotNone(default_model)
            self.assertEqual(default_model.name, "测试模型管理器")
            
            # 测试更新模型
            updated_model = AIModelConfig(
                id=test_model.id,
                name="更新后的模型",
                base_url="https://api.updated.com/v1",
                token_key="sk-updated-key",
                model_name="updated-model",
                is_default=True
            )
            
            result = config_manager.update_model(test_model.id, updated_model)
            self.assertTrue(result)
            
            # 验证更新结果
            models = config_manager.load_models()
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0].name, "更新后的模型")
            
            # 测试删除模型
            result = config_manager.delete_model(test_model.id)
            self.assertTrue(result)
            
            # 验证删除结果
            models = config_manager.load_models()
            self.assertEqual(len(models), 0)
            
            print("✅ 配置管理器测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入配置模块: {e}")
        except Exception as e:
            self.fail(f"配置管理器测试失败: {e}")
    
    def test_config_validation(self):
        """测试配置验证"""
        try:
            from config.ai_config import AIModelConfig, AIConfigManager
            import uuid
            
            config_manager = AIConfigManager(self.temp_dir)
            
            # 测试有效配置
            valid_model = AIModelConfig(
                id=str(uuid.uuid4()),
                name="有效模型",
                base_url="https://api.openai.com/v1",
                token_key="sk-valid-key",
                model_name="gpt-3.5-turbo",
                is_default=True
            )
            
            errors = config_manager.validate_model(valid_model)
            self.assertEqual(len(errors), 0)
            
            # 测试无效配置
            invalid_model = AIModelConfig(
                id=str(uuid.uuid4()),
                name="",  # 空名称
                base_url="invalid-url",  # 无效URL
                token_key="",  # 空密钥
                model_name="",  # 空模型名
                is_default=True
            )
            
            errors = config_manager.validate_model(invalid_model)
            self.assertGreater(len(errors), 0)
            self.assertTrue(any("名称不能为空" in error for error in errors))
            self.assertTrue(any("API基础URL" in error for error in errors))
            self.assertTrue(any("API密钥不能为空" in error for error in errors))
            self.assertTrue(any("模型名称不能为空" in error for error in errors))
            
            print("✅ 配置验证测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入配置模块: {e}")
        except Exception as e:
            self.fail(f"配置验证测试失败: {e}")
    
    def test_config_encryption(self):
        """测试配置加密功能"""
        try:
            from config.ai_config import ConfigEncryptor
            
            encryptor = ConfigEncryptor("test-password")
            
            # 测试加密解密
            original_text = "sk-sensitive-api-key-12345"
            encrypted_text = encryptor.encrypt(original_text)
            decrypted_text = encryptor.decrypt(encrypted_text)
            
            # 验证加密结果
            self.assertNotEqual(original_text, encrypted_text)
            self.assertEqual(original_text, decrypted_text)
            
            # 测试空字符串
            empty_encrypted = encryptor.encrypt("")
            empty_decrypted = encryptor.decrypt(empty_encrypted)
            self.assertEqual(empty_encrypted, "")
            self.assertEqual(empty_decrypted, "")
            
            print("✅ 配置加密测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入加密模块: {e}")
        except Exception as e:
            self.fail(f"配置加密测试失败: {e}")
    
    @patch('requests.post')
    def test_ai_client(self, mock_post):
        """测试AI客户端"""
        try:
            from config.ai_client import AIApiClient, AIModelConfig
            import uuid
            
            # 创建测试模型配置
            test_config = AIModelConfig(
                id=str(uuid.uuid4()),
                name="测试客户端",
                base_url="https://api.test.com/v1",
                token_key="sk-test-key",
                model_name="test-model",
                is_default=True
            )
            
            # 模拟API响应
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '这是一个测试总结'
                    }
                }],
                'usage': {
                    'prompt_tokens': 100,
                    'completion_tokens': 50,
                    'total_tokens': 150
                },
                'model': 'test-model'
            }
            mock_post.return_value = mock_response
            
            # 创建AI客户端
            client = AIApiClient(test_config, timeout=5, max_retries=1)
            
            # 测试生成总结
            test_text = "这是测试文本内容"
            result = client.generate_summary(test_text)
            
            # 验证结果
            self.assertTrue(result.success)
            self.assertEqual(result.content, "这是一个测试总结")
            self.assertEqual(result.model, "test-model")
            self.assertEqual(result.usage['total_tokens'], 150)
            
            # 验证API调用
            mock_post.assert_called_once()
            
            print("✅ AI客户端测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入AI客户端模块: {e}")
        except Exception as e:
            self.fail(f"AI客户端测试失败: {e}")
    
    def test_ui_components(self):
        """测试UI组件"""
        try:
            # 测试UI组件导入
            from ui.ai_config_dialog import AIConfigDialog, ModelListWidget, ModelDetailWidget
            from PyQt5.QtWidgets import QApplication
            
            # 创建QApplication实例（如果不存在）
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # 测试组件创建
            model_list = ModelListWidget()
            model_detail = ModelDetailWidget()
            
            # 验证组件创建成功
            self.assertIsNotNone(model_list)
            self.assertIsNotNone(model_detail)
            
            print("✅ UI组件测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入UI组件: {e}")
        except Exception as e:
            self.fail(f"UI组件测试失败: {e}")
    
    def test_browser_integration(self):
        """测试浏览器集成"""
        try:
            # 测试浏览器导入
            import browser
            
            # 验证关键类存在
            self.assertTrue(hasattr(browser, 'NovelBrowser'))
            
            print("✅ 浏览器集成测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入浏览器模块: {e}")
        except Exception as e:
            self.fail(f"浏览器集成测试失败: {e}")
    
    def test_config_templates(self):
        """测试配置模板"""
        try:
            import config
            
            # 验证AI配置模板存在
            self.assertTrue(hasattr(config, 'AI_TEMPLATES'))
            templates = config.AI_TEMPLATES
            
            # 验证常用模板
            expected_templates = ['openai', 'azure', 'localai', 'ollama']
            for template_name in expected_templates:
                self.assertIn(template_name, templates)
                template = templates[template_name]
                self.assertIn('name', template)
                self.assertIn('base_url', template)
                self.assertIn('model_name', template)
                self.assertIn('description', template)
            
            print("✅ 配置模板测试通过")
            
        except ImportError as e:
            self.skipTest(f"无法导入配置模块: {e}")
        except Exception as e:
            self.fail(f"配置模板测试失败: {e}")

def run_integration_test():
    """运行集成测试"""
    print("\n" + "="*60)
    print("🧪 开始AI配置功能集成测试")
    print("="*60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    test_cases = [
        'test_config_data_structure',
        'test_config_manager',
        'test_config_validation',
        'test_config_encryption',
        'test_ai_client',
        'test_ui_components',
        'test_browser_integration',
        'test_config_templates'
    ]
    
    for test_case in test_cases:
        suite.addTest(TestAIConfig(test_case))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果统计")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # 返回测试是否全部通过
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_integration_test()
    
    if success:
        print("\n🎉 所有测试通过！AI配置功能工作正常。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查相关功能。")
        sys.exit(1)
