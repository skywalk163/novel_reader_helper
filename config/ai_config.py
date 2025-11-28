#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置管理模块
提供AI模型配置的存储、加载、增删改查等功能
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import hashlib
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("警告: cryptography库未安装，将使用明文存储API密钥")

@dataclass
class AIModelConfig:
    """AI模型配置数据类"""
    id: str  # 唯一标识
    name: str  # 模型显示名称
    base_url: str  # API基础URL
    token_key: str  # API密钥（加密存储）
    model_name: str  # 模型名称（如gpt-3.5-turbo）
    is_default: bool = False  # 是否为默认模型
    created_at: str = None  # 创建时间（ISO格式）
    updated_at: str = None  # 更新时间（ISO格式）
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class ConfigEncryptor:
    """配置加密器，用于加密/解密敏感信息"""
    
    def __init__(self, password: str = None):
        """初始化加密器
        
        Args:
            password: 加密密码，如果为None则使用默认密码
        """
        if not CRYPTO_AVAILABLE:
            self.cipher = None
            return
        
        if password is None:
            # 使用默认密码（基于机器特征生成）
            machine_id = self._get_machine_id()
            password = f"novel_reader_ai_config_{machine_id}"
        
        # 生成加密密钥
        salt = b'novel_reader_salt'  # 固定盐值，确保一致性
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
    
    def _get_machine_id(self) -> str:
        """获取机器唯一标识"""
        try:
            import platform
            system_info = platform.platform()
            processor = platform.processor()
            machine = platform.machine()
            
            # 组合系统信息生成唯一标识
            combined = f"{system_info}_{processor}_{machine}"
            return hashlib.md5(combined.encode()).hexdigest()[:16]
        except:
            return "default_machine"
    
    def encrypt(self, text: str) -> str:
        """加密文本
        
        Args:
            text: 要加密的文本
            
        Returns:
            加密后的base64字符串
        """
        if not text:
            return ""
        
        if not self.cipher:
            # 如果加密不可用，返回原文
            return text
        
        try:
            encrypted = self.cipher.encrypt(text.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"加密失败: {e}")
            return text  # 加密失败时返回原文
    
    def decrypt(self, encrypted_text: str) -> str:
        """解密文本
        
        Args:
            encrypted_text: 加密的base64字符串
            
        Returns:
            解密后的原始文本
        """
        if not encrypted_text:
            return ""
        
        if not self.cipher:
            # 如果加密不可用，返回原文
            return encrypted_text
        
        try:
            # 如果不是base64格式，可能是未加密的文本
            try:
                encrypted = base64.b64decode(encrypted_text.encode())
                decrypted = self.cipher.decrypt(encrypted)
                return decrypted.decode()
            except (base64.binascii.Error, ValueError):
                # 解密失败，可能是未加密的文本
                return encrypted_text
        except Exception as e:
            print(f"解密失败: {e}")
            return encrypted_text  # 解密失败时返回原文本

class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "ai_models.json")
        self.backup_dir = os.path.join(config_dir, "backups")
        self.encryptor = ConfigEncryptor()
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 内存中的配置缓存
        self._models_cache: Optional[List[AIModelConfig]] = None
    
    def load_models(self) -> List[AIModelConfig]:
        """加载所有AI模型配置
        
        Returns:
            AI模型配置列表
        """
        if self._models_cache is not None:
            return self._models_cache
        
        models = []
        
        if not os.path.exists(self.config_file):
            # 配置文件不存在，返回空列表
            self._models_cache = models
            return models
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data.get('models', []):
                try:
                    # 解密token_key
                    encrypted_token = item.get('token_key', '')
                    decrypted_token = self.encryptor.decrypt(encrypted_token)
                    
                    model = AIModelConfig(
                        id=item['id'],
                        name=item['name'],
                        base_url=item['base_url'],
                        token_key=decrypted_token,
                        model_name=item['model_name'],
                        is_default=item.get('is_default', False),
                        created_at=item.get('created_at', ''),
                        updated_at=item.get('updated_at', '')
                    )
                    models.append(model)
                except Exception as e:
                    print(f"加载模型配置失败: {e}, 数据: {item}")
                    continue
            
            self._models_cache = models
            print(f"成功加载 {len(models)} 个AI模型配置")
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 尝试加载备份
            models = self._load_from_backup()
            self._models_cache = models
        
        return models
    
    def save_models(self, models: List[AIModelConfig]) -> bool:
        """保存所有AI模型配置
        
        Args:
            models: AI模型配置列表
            
        Returns:
            保存是否成功
        """
        try:
            # 创建备份
            self._create_backup()
            
            # 准备保存数据
            data = {
                'version': '1.0',
                'models': []
            }
            
            for model in models:
                # 加密token_key
                encrypted_token = self.encryptor.encrypt(model.token_key)
                
                model_data = asdict(model)
                model_data['token_key'] = encrypted_token
                data['models'].append(model_data)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            self._models_cache = models
            
            print(f"成功保存 {len(models)} 个AI模型配置")
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_default_model(self) -> Optional[AIModelConfig]:
        """获取默认AI模型
        
        Returns:
            默认AI模型配置，如果没有则返回None
        """
        models = self.load_models()
        for model in models:
            if model.is_default:
                return model
        return None
    
    def set_default_model(self, model_id: str) -> bool:
        """设置默认AI模型
        
        Args:
            model_id: 模型ID
            
        Returns:
            设置是否成功
        """
        models = self.load_models()
        
        # 清除所有默认标记
        for model in models:
            if model.is_default:
                model.is_default = False
                model.updated_at = datetime.now().isoformat()
        
        # 设置新的默认模型
        for model in models:
            if model.id == model_id:
                model.is_default = True
                model.updated_at = datetime.now().isoformat()
                return self.save_models(models)
        
        return False
    
    def add_model(self, model: AIModelConfig) -> bool:
        """添加AI模型
        
        Args:
            model: AI模型配置
            
        Returns:
            添加是否成功
        """
        models = self.load_models()
        
        # 检查ID是否已存在
        for existing_model in models:
            if existing_model.id == model.id:
                print(f"模型ID {model.id} 已存在")
                return False
        
        # 如果这是第一个模型，设为默认
        if not models:
            model.is_default = True
        
        # 如果设置为新默认，清除其他默认标记
        if model.is_default:
            for existing_model in models:
                existing_model.is_default = False
                existing_model.updated_at = datetime.now().isoformat()
        
        models.append(model)
        return self.save_models(models)
    
    def update_model(self, model_id: str, updated_model: AIModelConfig) -> bool:
        """更新AI模型
        
        Args:
            model_id: 要更新的模型ID
            updated_model: 更新后的模型配置
            
        Returns:
            更新是否成功
        """
        models = self.load_models()
        
        for i, model in enumerate(models):
            if model.id == model_id:
                # 保持ID和创建时间不变
                updated_model.id = model_id
                updated_model.created_at = model.created_at
                updated_model.updated_at = datetime.now().isoformat()
                
                # 如果设置为新默认，清除其他默认标记
                if updated_model.is_default:
                    for other_model in models:
                        if other_model.id != model_id:
                            other_model.is_default = False
                            other_model.updated_at = datetime.now().isoformat()
                
                models[i] = updated_model
                return self.save_models(models)
        
        print(f"未找到ID为 {model_id} 的模型")
        return False
    
    def delete_model(self, model_id: str) -> bool:
        """删除AI模型
        
        Args:
            model_id: 要删除的模型ID
            
        Returns:
            删除是否成功
        """
        models = self.load_models()
        
        deleted_model = None
        new_models = []
        
        for model in models:
            if model.id == model_id:
                deleted_model = model
            else:
                new_models.append(model)
        
        if deleted_model is None:
            print(f"未找到ID为 {model_id} 的模型")
            return False
        
        # 如果删除的是默认模型，设置第一个为默认
        if deleted_model.is_default and new_models:
            new_models[0].is_default = True
            new_models[0].updated_at = datetime.now().isoformat()
        
        return self.save_models(new_models)
    
    def validate_model(self, model: AIModelConfig) -> List[str]:
        """验证模型配置
        
        Args:
            model: 要验证的模型配置
            
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        if not model.name or model.name.strip() == "":
            errors.append("模型名称不能为空")
        
        if not model.base_url or model.base_url.strip() == "":
            errors.append("API基础URL不能为空")
        elif not (model.base_url.startswith('http://') or model.base_url.startswith('https://')):
            errors.append("API基础URL必须以http://或https://开头")
        
        if not model.token_key or model.token_key.strip() == "":
            errors.append("API密钥不能为空")
        
        if not model.model_name or model.model_name.strip() == "":
            errors.append("模型名称不能为空")
        
        return errors
    
    def _create_backup(self) -> bool:
        """创建配置文件备份
        
        Returns:
            备份是否成功
        """
        if not os.path.exists(self.config_file):
            return True
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f"ai_models_{timestamp}.json")
            
            # 复制文件
            with open(self.config_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            # 清理旧备份（保留最近10个）
            self._cleanup_old_backups()
            
            print(f"创建备份文件: {backup_file}")
            return True
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return False
    
    def _load_from_backup(self) -> List[AIModelConfig]:
        """从备份文件加载配置
        
        Returns:
            加载的模型配置列表
        """
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith('ai_models_') and f.endswith('.json')]
            
            if not backup_files:
                return []
            
            # 按时间排序，取最新的
            backup_files.sort(reverse=True)
            latest_backup = os.path.join(self.backup_dir, backup_files[0])
            
            with open(latest_backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            models = []
            for item in data.get('models', []):
                # 解密token_key
                encrypted_token = item.get('token_key', '')
                decrypted_token = self.encryptor.decrypt(encrypted_token)
                
                model = AIModelConfig(
                    id=item['id'],
                    name=item['name'],
                    base_url=item['base_url'],
                    token_key=decrypted_token,
                    model_name=item['model_name'],
                    is_default=item.get('is_default', False),
                    created_at=item.get('created_at', ''),
                    updated_at=item.get('updated_at', '')
                )
                models.append(model)
            
            print(f"从备份文件加载 {len(models)} 个模型配置: {backup_files[0]}")
            return models
            
        except Exception as e:
            print(f"从备份加载失败: {e}")
            return []
    
    def _cleanup_old_backups(self):
        """清理旧的备份文件，保留最近10个"""
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith('ai_models_') and f.endswith('.json')]
            
            if len(backup_files) <= 10:
                return
            
            # 按时间排序，删除最旧的
            backup_files.sort()
            files_to_delete = backup_files[:-10]
            
            for file_name in files_to_delete:
                file_path = os.path.join(self.backup_dir, file_name)
                os.remove(file_path)
                print(f"删除旧备份文件: {file_name}")
                
        except Exception as e:
            print(f"清理备份文件失败: {e}")
    
    def clear_cache(self):
        """清除内存缓存"""
        self._models_cache = None

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> AIConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager

if __name__ == "__main__":
    # 测试代码
    manager = AIConfigManager()
    
    # 创建测试模型
    test_model = AIModelConfig(
        id=str(uuid.uuid4()),
        name="测试模型",
        base_url="https://api.openai.com/v1",
        token_key="sk-test-key-12345",
        model_name="gpt-3.5-turbo",
        is_default=True
    )
    
    # 测试添加
    print("测试添加模型...")
    success = manager.add_model(test_model)
    print(f"添加结果: {success}")
    
    # 测试加载
    print("\n测试加载模型...")
    models = manager.load_models()
    print(f"加载到 {len(models)} 个模型")
    for model in models:
        print(f"模型: {model.name}, URL: {model.base_url}, 默认: {model.is_default}")
    
    # 测试默认模型
    print("\n测试默认模型...")
    default_model = manager.get_default_model()
    if default_model:
        print(f"默认模型: {default_model.name}")
    else:
        print("没有默认模型")
    
    print("\n测试完成！")
