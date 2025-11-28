# AI大模型配置功能需求文档

## 需求背景
当前小说阅读神器的AI总结功能使用基于规则的简单算法，总结效果有限。为了提供更智能、更准确的文本总结功能，需要集成OpenAI兼容的AI大模型服务，让用户可以配置和使用不同的AI模型来进行内容分析和总结。

## 用户故事
作为小说阅读神器的用户，我希望能够：
1. 配置多个OpenAI兼容的AI大模型服务
2. 设置每个模型的base_url、API密钥和模型名称
3. 选择其中一个模型作为默认使用
4. 在进行"AI总结"时，优先使用配置的AI大模型进行智能总结
5. 在AI模型不可用时，能够回退到原有的基于规则的总结方式

## 使用场景
### 场景1：配置AI模型
- 用户点击"配置"按钮进入配置界面
- 在配置界面中添加AI模型信息（base_url、token_key、模型名称）
- 可以添加多个模型配置
- 设置其中一个为默认模型
- 保存配置并返回主界面

### 场景2：使用AI总结
- 用户先提取小说内容
- 点击"AI总结"按钮
- 系统检查是否有配置的默认AI模型
- 如果有，调用AI模型进行总结
- 如果AI模型调用失败，回退到基于规则的总结
- 显示总结结果给用户

### 场景3：模型管理
- 用户可以编辑已配置的模型信息
- 可以删除不需要的模型配置
- 可以切换默认模型
- 可以测试模型连接是否正常

## 技术方案

### 1. 数据模型设计
```python
# AI模型配置数据结构
class AIModelConfig:
    id: str  # 唯一标识
    name: str  # 模型显示名称
    base_url: str  # API基础URL
    token_key: str  # API密钥
    model_name: str  # 模型名称（如gpt-3.5-turbo）
    is_default: bool  # 是否为默认模型
    created_at: datetime  # 创建时间
    updated_at: datetime  # 更新时间
```

### 2. 配置存储方案
- 使用JSON文件存储配置信息
- 配置文件路径：`config/ai_models.json`
- 对API密钥进行简单的加密存储
- 提供配置备份和恢复功能

### 3. UI设计方案
#### 配置按钮
- 在主工具栏添加"⚙️ AI配置"按钮
- 按钮位置：在"AI总结"按钮旁边
- 图标使用齿轮符号，易于识别

#### 配置对话框
- 使用QDialog创建配置界面
- 左侧显示模型列表，右侧显示模型详情
- 提供添加、编辑、删除、设为默认按钮
- 包含测试连接功能

#### AI总结增强
- 在原有AI总结功能基础上增加AI模型调用
- 保持与现有功能的兼容性
- 添加模型选择下拉框（可选）

### 4. API集成方案
```python
class AIApiClient:
    def __init__(self, base_url, token_key, model_name):
        self.base_url = base_url
        self.token_key = token_key
        self.model_name = model_name
    
    def generate_summary(self, text, max_tokens=500):
        """调用AI API生成文本总结"""
        prompt = f"请对以下小说章节内容进行总结，提取主要情节和关键信息：\n\n{text}"
        # 调用OpenAI兼容API
```

### 5. 错误处理策略
- 网络连接错误处理
- API认证失败处理
- 模型调用超时处理
- 优雅降级到原有总结方式
- 用户友好的错误提示

## 实现细节

### 1. 配置管理模块
```python
# config/ai_config.py
class AIConfigManager:
    def load_models(self) -> List[AIModelConfig]
    def save_models(self, models: List[AIModelConfig])
    def get_default_model(self) -> Optional[AIModelConfig]
    def set_default_model(self, model_id: str)
    def add_model(self, model: AIModelConfig)
    def update_model(self, model_id: str, model: AIModelConfig)
    def delete_model(self, model_id: str)
```

### 2. UI组件设计
- AIConfigDialog: 配置对话框主类
- ModelListWidget: 模型列表组件
- ModelDetailWidget: 模型详情编辑组件
- TestConnectionDialog: 测试连接结果对话框

### 3. 主程序集成
- 在browser.py中集成配置功能
- 修改ai_summarize_content方法支持AI模型
- 添加配置状态指示

### 4. 数据流设计
```
用户点击配置按钮 → 打开配置对话框 → 加载现有配置 → 用户编辑 → 保存配置 → 更新内存配置
用户点击AI总结 → 检查默认模型 → 调用AI API → 处理响应 → 显示结果
```

### 5. 接口设计
#### 配置接口
```python
def show_ai_config_dialog(self):
    """显示AI配置对话框"""

def on_config_updated(self):
    """配置更新后的回调"""
```

#### AI总结接口
```python
def ai_summarize_with_model(self, text: str, model_config: AIModelConfig) -> str:
    """使用指定AI模型进行总结"""

def fallback_to_rule_summary(self, text: str) -> str:
    """回退到基于规则的总结"""
```

## 预期成果

### 1. 功能完整性
- ✅ 支持配置多个OpenAI兼容的AI模型
- ✅ 提供友好的配置界面
- ✅ 实现智能AI总结功能
- ✅ 保持向后兼容性
- ✅ 完善的错误处理机制

### 2. 用户体验
- 配置流程简单直观
- AI总结效果显著提升
- 操作响应快速流畅
- 错误提示清晰友好

### 3. 技术指标
- 配置数据安全存储
- API调用稳定可靠
- 界面响应时间 < 2秒
- AI总结生成时间 < 10秒

### 4. 扩展性
- 易于添加新的AI模型提供商
- 支持更多AI功能扩展
- 配置格式版本兼容

## 风险评估

### 1. 技术风险
- **风险**：不同AI服务商API格式差异
- **应对**：标准化API调用接口，适配主流服务商

### 2. 安全风险
- **风险**：API密钥泄露
- **应对**：本地加密存储，不上传云端

### 3. 兼容性风险
- **风险**：影响现有功能
- **应对**：保持原有功能不变，新增功能独立实现

## 开发计划

### 阶段1：核心功能开发
- 配置管理模块
- AI API客户端
- 基础UI组件

### 阶段2：界面集成
- 配置对话框
- 主界面集成
- 交互逻辑

### 阶段3：功能完善
- 错误处理
- 用户体验优化
- 测试和调试

### 阶段4：测试验证
- 功能测试
- 兼容性测试
- 用户体验测试

### 阶段5：收尾
- 依赖库等进行相应修改
- readme说明进行相应修改