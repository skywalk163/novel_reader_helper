# 配置模块包初始化文件

# 定义版本信息
__version__ = "1.0.0"

# 尝试导入主要模块
try:
    # 尝试直接导入文件
    import sys
    import os
    
    # 获取当前目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 添加到Python路径
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 直接导入文件模块
    import ai_config
    import ai_client
    
    # 导出主要类和函数
    AIModelConfig = ai_config.AIModelConfig
    AIConfigManager = ai_config.AIConfigManager
    get_config_manager = ai_config.get_config_manager
    AIApiClient = ai_client.AIApiClient
    AIModelManager = ai_client.AIModelManager
    APIResponse = ai_client.APIResponse
    
    __all__ = [
        'AIModelConfig',
        'AIConfigManager', 
        'get_config_manager',
        'AIApiClient',
        'AIModelManager',
        'APIResponse',
        '__version__'
    ]
    
    print("✅ 配置模块导入成功")
    
except ImportError as e:
    print(f"⚠️ 配置模块导入失败，使用降级模式: {e}")
    
    # 提供默认的空类以避免程序崩溃
    class AIModelConfig:
        def __init__(self, *args, **kwargs):
            self.id = kwargs.get('id', 'default-id')
            self.name = kwargs.get('name', '默认模型')
            self.base_url = kwargs.get('base_url', '')
            self.token_key = kwargs.get('token_key', '')
            self.model_name = kwargs.get('model_name', '')
            self.is_default = kwargs.get('is_default', False)
            self.created_at = kwargs.get('created_at', '')
            self.updated_at = kwargs.get('updated_at', '')
    
    class AIConfigManager:
        def __init__(self, *args, **kwargs):
            pass
    
    def get_config_manager():
        return None
    
    class AIApiClient:
        def __init__(self, *args, **kwargs):
            pass
    
    class AIModelManager:
        @staticmethod
        def test_model(model_config):
            class MockResponse:
                success = False
                error_message = "配置模块不可用，请检查ai_config模块是否正确安装"
                response_time = 0.0
                error_code = "MODULE_NOT_AVAILABLE"
            return MockResponse()
    
    class APIResponse:
        def __init__(self, *args, **kwargs):
            self.success = kwargs.get('success', False)
            self.content = kwargs.get('content', '')
            self.model = kwargs.get('model', '')
            self.usage = kwargs.get('usage', {})
            self.error_message = kwargs.get('error_message', '')
            self.error_code = kwargs.get('error_code', '')
            self.response_time = kwargs.get('response_time', 0.0)
    
    __all__ = [
        'AIModelConfig',
        'AIConfigManager', 
        'get_config_manager',
        'AIApiClient',
        'AIModelManager',
        'APIResponse',
        '__version__'
    ]
