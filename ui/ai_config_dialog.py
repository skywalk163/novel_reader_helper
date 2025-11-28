#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置对话框UI组件
提供AI模型配置的图形界面
"""

import sys
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QGroupBox,
    QCheckBox, QMessageBox, QSplitter, QFrame, QProgressBar, QComboBox,
    QSpinBox, QTabWidget, QWidget, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap

try:
    from config.ai_config import AIModelConfig, get_config_manager
    from config.ai_client import AIModelManager, APIResponse
except ImportError as e:
    print(f"警告: 无法导入AI配置模块: {e}")
    # 提供默认的AIModelConfig类以避免程序崩溃
    class AIModelConfig:
        def __init__(self, *args, **kwargs):
            # 设置默认属性，确保对象有所有必要的属性
            self.id = kwargs.get('id', 'default-id')
            self.name = kwargs.get('name', '默认模型')
            self.base_url = kwargs.get('base_url', '')
            self.token_key = kwargs.get('token_key', '')
            self.model_name = kwargs.get('model_name', '')
            self.is_default = kwargs.get('is_default', False)
            self.created_at = kwargs.get('created_at', '')
            self.updated_at = kwargs.get('updated_at', '')
    
    def get_config_manager():
        return None
    
    class AIModelManager:
        @staticmethod
        def test_model(model_config):
            class MockResponse:
                success = False
                error_message = "AI配置模块不可用，请检查ai_config模块是否正确安装"
                response_time = 0.0
                error_code = "MODULE_NOT_AVAILABLE"
            return MockResponse()
    
    class APIResponse:
        pass

class TestConnectionThread(QThread):
    """测试连接的工作线程"""
    
    finished = pyqtSignal(APIResponse)
    
    def __init__(self, model_config: AIModelConfig):
        super().__init__()
        self.model_config = model_config
    
    def run(self):
        """执行连接测试"""
        result = AIModelManager.test_model(self.model_config)
        self.finished.emit(result)

class ModelDetailWidget(QWidget):
    """模型详情编辑组件"""
    
    config_changed = pyqtSignal()  # 配置变更信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_model: Optional[AIModelConfig] = None
        self.is_new_model = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入模型显示名称，如：ChatGPT-3.5")
        self.name_edit.textChanged.connect(self._on_config_changed)
        basic_layout.addRow("模型名称:", self.name_edit)
        
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("输入模型名称，如：gpt-3.5-turbo")
        self.model_name_edit.textChanged.connect(self._on_config_changed)
        basic_layout.addRow("API模型:", self.model_name_edit)
        
        self.default_checkbox = QCheckBox("设为默认模型")
        self.default_checkbox.stateChanged.connect(self._on_config_changed)
        basic_layout.addRow("", self.default_checkbox)
        
        layout.addWidget(basic_group)
        
        # API配置组
        api_group = QGroupBox("API配置")
        api_layout = QFormLayout(api_group)
        
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("输入API基础URL，如：https://api.openai.com/v1")
        self.base_url_edit.textChanged.connect(self._on_config_changed)
        api_layout.addRow("Base URL:", self.base_url_edit)
        
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("输入API密钥，如：sk-xxxxxxxx")
        self.token_edit.textChanged.connect(self._on_config_changed)
        api_layout.addRow("API密钥:", self.token_edit)
        
        layout.addWidget(api_group)
        
        # 常用配置模板
        template_group = QGroupBox("常用配置模板")
        template_layout = QFormLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("自定义配置", "")
        self.template_combo.addItem("OpenAI", "openai")
        self.template_combo.addItem("Azure OpenAI", "azure")
        self.template_combo.addItem("LocalAI", "localai")
        self.template_combo.addItem("Ollama", "ollama")
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        template_layout.addRow("配置模板:", self.template_combo)
        
        layout.addWidget(template_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("🔗 测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setEnabled(False)
        button_layout.addWidget(self.test_btn)
        
        self.save_btn = QPushButton("💾 保存配置")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.reset_form)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # 测试结果区域
        self.test_result_text = QTextEdit()
        self.test_result_text.setMaximumHeight(100)
        self.test_result_text.setPlaceholderText("测试结果将显示在这里...")
        self.test_result_text.setReadOnly(True)
        layout.addWidget(QLabel("连接测试结果:"))
        layout.addWidget(self.test_result_text)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 初始状态
        self.set_model(None)
    
    def _on_config_changed(self):
        """配置变更时的处理"""
        self.save_btn.setEnabled(True)
        self.test_btn.setEnabled(self._can_test_connection())
    
    def _on_template_changed(self, index: int):
        """模板选择变更时的处理"""
        template_data = self.template_combo.itemData(index)
        
        if not template_data:
            return
        
        try:
            # 直接定义AI模板，避免导入问题
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
            
            if template_data in AI_TEMPLATES:
                template = AI_TEMPLATES[template_data]
                
                # 如果当前表单为空，则填充模板
                if not self.name_edit.text().strip():
                    self.name_edit.setText(template["name"])
                if not self.base_url_edit.text().strip():
                    self.base_url_edit.setText(template["base_url"])
                if not self.model_name_edit.text().strip():
                    self.model_name_edit.setText(template["model_name"])
        
        except Exception as e:
            print(f"模板处理出错: {e}")
            # 出错时静默处理，不影响用户体验
    
    def _can_test_connection(self) -> bool:
        """检查是否可以进行连接测试"""
        try:
            name_text = self.name_edit.text().strip() if hasattr(self, 'name_edit') and self.name_edit else ""
            url_text = self.base_url_edit.text().strip() if hasattr(self, 'base_url_edit') and self.base_url_edit else ""
            token_text = self.token_edit.text().strip() if hasattr(self, 'token_edit') and self.token_edit else ""
            model_text = self.model_name_edit.text().strip() if hasattr(self, 'model_name_edit') and self.model_name_edit else ""
            
            name_filled = bool(name_text)
            url_filled = bool(url_text)
            token_filled = bool(token_text)
            model_filled = bool(model_text)
            
            result = name_filled and url_filled and token_filled and model_filled
            print(f"🔧 DEBUG: _can_test_connection返回: {result} (类型: {type(result)})")
            return result
        except Exception as e:
            print(f"🔧 DEBUG: _can_test_connection异常: {e}")
            return False
    
    def set_model(self, model: Optional[AIModelConfig], is_new: bool = False):
        """设置当前编辑的模型
        
        Args:
            model: 模型配置，None表示新建
            is_new: 是否为新建模型
        """
        self.current_model = model
        self.is_new_model = is_new
        
        if model:
            # 编辑现有模型
            self.name_edit.setText(model.name)
            self.base_url_edit.setText(model.base_url)
            self.token_edit.setText(model.token_key)
            self.model_name_edit.setText(model.model_name)
            self.default_checkbox.setChecked(model.is_default)
            self.template_combo.setCurrentIndex(0)  # 重置为自定义
        else:
            # 新建模型
            self.reset_form()
        
        self.save_btn.setEnabled(False)
        self.test_btn.setEnabled(self._can_test_connection())
        self.test_result_text.clear()
    
    def get_model(self) -> Optional[AIModelConfig]:
        """获取当前表单的模型配置
        
        Returns:
            模型配置对象，如果验证失败返回None
        """
        if not self._can_test_connection():
            return None
        
        if self.current_model and not self.is_new_model:
            # 编辑现有模型
            model = self.current_model
            model.name = self.name_edit.text().strip()
            model.base_url = self.base_url_edit.text().strip()
            model.token_key = self.token_edit.text().strip()
            model.model_name = self.model_name_edit.text().strip()
            model.is_default = self.default_checkbox.isChecked()
        else:
            # 新建模型
            import uuid
            from datetime import datetime
            
            model = AIModelConfig(
                id=str(uuid.uuid4()),
                name=self.name_edit.text().strip(),
                base_url=self.base_url_edit.text().strip(),
                token_key=self.token_edit.text().strip(),
                model_name=self.model_name_edit.text().strip(),
                is_default=self.default_checkbox.isChecked(),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        
        # 验证配置
        config_manager = get_config_manager()
        if config_manager is None:
            # 配置管理器不可用，跳过验证
            print("🔧 DEBUG: 配置管理器不可用，跳过验证")
            return model
        
        try:
            errors = config_manager.validate_model(model)
            
            if errors:
                QMessageBox.warning(self, "配置验证失败", "\n".join(errors))
                return None
        except Exception as e:
            print(f"?? DEBUG: 验证模型配置时出错: {e}")
            # 验证失败时，仍然返回模型，让用户自行决定
        
        return model
    
    def test_connection(self):
        """测试连接"""
        if not self._can_test_connection():
            QMessageBox.warning(self, "提示", "请先填写完整的配置信息")
            return
        
        model = self.get_model()
        if not model:
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("🔄 测试中...")
        self.test_result_text.setText("正在测试连接，请稍候...")
        
        # 启动测试线程
        self.test_thread = TestConnectionThread(model)
        self.test_thread.finished.connect(self._on_test_finished)
        self.test_thread.start()
    
    def _on_test_finished(self, result: APIResponse):
        """连接测试完成后的处理"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔗 测试连接")
        
        if result.success:
            success_text = f"✅ 连接成功！\n"
            success_text += f"响应时间: {result.response_time:.2f}秒\n"
            success_text += f"使用模型: {result.model}"
            
            self.test_result_text.setText(success_text)
            QMessageBox.information(self, "连接成功", "API连接测试成功！")
        else:
            error_text = f"❌ 连接失败！\n"
            error_text += f"错误信息: {result.error_message}\n"
            error_text += f"错误代码: {result.error_code}\n"
            error_text += f"响应时间: {result.response_time:.2f}秒"
            
            self.test_result_text.setText(error_text)
            QMessageBox.warning(self, "连接失败", f"API连接测试失败:\n{result.error_message}")
    
    def save_config(self):
        """保存配置"""
        model = self.get_model()
        if not model:
            return
        
        config_manager = get_config_manager()
        
        if config_manager is None:
            # 配置管理器不可用，显示提示
            QMessageBox.warning(self, "保存失败", "配置管理器不可用，请检查ai_config模块是否正确安装")
            return
        
        try:
            if self.current_model and not self.is_new_model:
                # 更新现有模型
                success = config_manager.update_model(self.current_model.id, model)
                action = "更新"
            else:
                # 添加新模型
                success = config_manager.add_model(model)
                action = "添加"
            
            if success:
                QMessageBox.information(self, "保存成功", f"模型配置{action}成功！")
                self.save_btn.setEnabled(False)
                self.config_changed.emit()
            else:
                QMessageBox.warning(self, "保存失败", f"模型配置{action}失败！")
                
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存配置时发生错误:\n{str(e)}")
    
    def reset_form(self):
        """重置表单"""
        self.name_edit.clear()
        self.base_url_edit.clear()
        self.token_edit.clear()
        self.model_name_edit.clear()
        self.default_checkbox.setChecked(False)
        self.template_combo.setCurrentIndex(0)
        self.test_result_text.clear()
        self.save_btn.setEnabled(False)
        self.test_btn.setEnabled(False)

class ModelListWidget(QWidget):
    """模型列表组件"""
    
    model_selected = pyqtSignal(str)  # 模型选择信号
    model_deleted = pyqtSignal(str)   # 模型删除信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_model_id: Optional[str] = None
        self.setup_ui()
        try:
            self.load_models()
        except Exception as e:
            print(f"🔧 DEBUG: ModelListWidget初始化时load_models出错: {e}")
            # 即使加载失败也要初始化界面
            pass
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 标题和按钮
        header_layout = QHBoxLayout()
        
        title_label = QLabel("已配置的AI模型")
        title_label.setFont(QFont("", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ 添加模型")
        self.add_btn.clicked.connect(self.add_new_model)
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)
        
        # 模型列表
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self.edit_current_model)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_current_model)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        self.set_default_btn = QPushButton("⭐ 设为默认")
        self.set_default_btn.clicked.connect(self.set_current_as_default)
        self.set_default_btn.setEnabled(False)
        button_layout.addWidget(self.set_default_btn)
        
        layout.addLayout(button_layout)
    
    def load_models(self):
        """加载模型列表"""
        self.list_widget.clear()
        self.current_model_id = None
        
        config_manager = get_config_manager()
        models = config_manager.load_models()
        
        for model in models:
            item_text = f"{model.name}"
            if model.is_default:
                item_text += " ⭐"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, model.id)
            
            if model.is_default:
                # 默认模型用粗体显示
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                # 设置背景色
                item.setBackground(Qt.lightGray)
            
            self.list_widget.addItem(item)
        
        # 更新按钮状态
        self._update_button_states()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """列表项点击事件"""
        model_id = item.data(Qt.UserRole)
        self.current_model_id = model_id
        self._update_button_states()
        self.model_selected.emit(model_id)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """列表项双击事件"""
        self.edit_current_model()
    
    def _update_button_states(self):
        """更新按钮状态"""
        has_selection = self.current_model_id is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.set_default_btn.setEnabled(has_selection)
    
    def add_new_model(self):
        """添加新模型"""
        self.current_model_id = None
        self._update_button_states()
        self.model_selected.emit("")  # 空字符串表示新建
    
    def edit_current_model(self):
        """编辑当前选中的模型"""
        if self.current_model_id:
            self.model_selected.emit(self.current_model_id)
    
    def delete_current_model(self):
        """删除当前选中的模型"""
        if not self.current_model_id:
            return
        
        config_manager = get_config_manager()
        models = config_manager.load_models()
        
        # 找到要删除的模型
        model_to_delete = None
        for model in models:
            if model.id == self.current_model_id:
                model_to_delete = model
                break
        
        if not model_to_delete:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除模型 \"{model_to_delete.name}\" 吗？\n\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = config_manager.delete_model(self.current_model_id)
                if success:
                    QMessageBox.information(self, "删除成功", "模型已成功删除")
                    self.model_deleted.emit(self.current_model_id)
                    self.load_models()
                else:
                    QMessageBox.warning(self, "删除失败", "删除模型时发生错误")
            except Exception as e:
                QMessageBox.critical(self, "删除错误", f"删除模型时发生错误:\n{str(e)}")
    
    def set_current_as_default(self):
        """设置当前模型为默认"""
        if not self.current_model_id:
            return
        
        config_manager = get_config_manager()
        
        try:
            success = config_manager.set_default_model(self.current_model_id)
            if success:
                QMessageBox.information(self, "设置成功", "已设置为默认模型")
                self.load_models()
                # 重新选中当前模型
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    if item.data(Qt.UserRole) == self.current_model_id:
                        self.list_widget.setCurrentItem(item)
                        break
            else:
                QMessageBox.warning(self, "设置失败", "设置默认模型时发生错误")
        except Exception as e:
            QMessageBox.critical(self, "设置错误", f"设置默认模型时发生错误:\n{str(e)}")

class AIConfigDialog(QDialog):
    """AI配置主对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI模型配置")
        self.setGeometry(200, 200, 900, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：模型列表
        self.model_list_widget = ModelListWidget()
        self.model_list_widget.model_selected.connect(self._on_model_selected)
        self.model_list_widget.model_deleted.connect(self._on_model_deleted)
        splitter.addWidget(self.model_list_widget)
        
        # 右侧：模型详情
        self.model_detail_widget = ModelDetailWidget()
        self.model_detail_widget.config_changed.connect(self._on_config_changed)
        splitter.addWidget(self.model_detail_widget)
        
        # 设置分割器比例
        splitter.setSizes([300, 600])
        layout.addWidget(splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_model_list)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def load_initial_data(self):
        """加载初始数据"""
        # 选择第一个模型或显示新建界面
        config_manager = get_config_manager()
        
        if config_manager is None:
            # 配置管理器不可用，显示新建界面
            self._on_model_selected("")  # 空字符串表示新建
            return
        
        try:
            models = config_manager.load_models()
            
            if models:
                # 如果有模型，选择第一个
                first_model_id = models[0].id
                self.model_list_widget.current_model_id = first_model_id
                self.model_list_widget._update_button_states()
                self._on_model_selected(first_model_id)
            else:
                # 如果没有模型，显示新建界面
                self._on_model_selected("")  # 空字符串表示新建
        except Exception as e:
            print(f"加载初始数据时出错: {e}")
            # 出错时显示新建界面
            self._on_model_selected("")
    
    def _on_model_selected(self, model_id: str):
        """模型选择事件处理"""
        config_manager = get_config_manager()
        
        if model_id:
            # 编辑现有模型
            models = config_manager.load_models()
            model = None
            for m in models:
                if m.id == model_id:
                    model = m
                    break
            
            if model:
                self.model_detail_widget.set_model(model, False)
        else:
            # 新建模型
            self.model_detail_widget.set_model(None, True)
    
    def _on_model_deleted(self, model_id: str):
        """模型删除事件处理"""
        # 如果删除的是当前编辑的模型，重置详情界面
        config_manager = get_config_manager()
        models = config_manager.load_models()
        
        if models:
            # 如果还有其他模型，选择第一个
            first_model_id = models[0].id
            self._on_model_selected(first_model_id)
            
            # 更新列表选择
            for i in range(self.model_list_widget.list_widget.count()):
                item = self.model_list_widget.list_widget.item(i)
                if item.data(Qt.UserRole) == first_model_id:
                    self.model_list_widget.list_widget.setCurrentItem(item)
                    break
        else:
            # 如果没有模型了，显示新建界面
            self._on_model_selected("")
    
    def _on_config_changed(self):
        """配置变更事件处理"""
        # 刷新模型列表以反映最新的默认模型状态
        try:
            config_manager = get_config_manager()
            if config_manager and hasattr(config_manager, 'load_models'):
                self.model_list_widget.load_models()
        except Exception as e:
            print(f"刷新模型列表时出错: {e}")
    
    def refresh_model_list(self):
        """刷新模型列表"""
        self.model_list_widget.load_models()
        QMessageBox.information(self, "刷新完成", "模型列表已刷新")

if __name__ == "__main__":
    # 测试代码
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = AIConfigDialog()
    dialog.show()
    
    sys.exit(app.exec_())
