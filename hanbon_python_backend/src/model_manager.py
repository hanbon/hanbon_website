#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: model_manager.py
@description: AI模型管理服务
@author: AI Assistant
@created: 2024
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, validator
import openai

logger = logging.getLogger(__name__)

class ModelConfig(BaseModel):
    """模型配置模型"""
    name: str
    model: str
    api_key: str
    api_base: str
    max_tokens: int = 16384
    temperature: float = 0.7
    supports_streaming: bool = True
    description: str = ""
    enabled: bool = True
    type: str = "custom"  # builtin 或 custom
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('温度值必须在0-2之间')
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError('最大令牌数必须大于0')
        return v

class ModelManager:
    """模型管理器类"""
    
    def __init__(self, config):
        """
        初始化模型管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.custom_models_file = Path(config.CUSTOM_MODELS_CONFIG_PATH)
        self.ai_clients = {}
        self._models_cache = {}
        self._init_builtin_models()
        self._load_custom_models()
    
    def _init_builtin_models(self):
        """初始化内置模型"""
        for model_id, model_config in self.config.AI_MODELS.items():
            if model_config.get('enabled', False) and model_config.get('api_key'):
                try:
                    self.ai_clients[model_id] = openai.AsyncOpenAI(
                        api_key=model_config['api_key'],
                        base_url=model_config['api_base']
                    )
                    self._models_cache[model_id] = model_config
                    logger.info(f"成功初始化内置模型: {model_config['name']}")
                except Exception as e:
                    logger.error(f"初始化内置模型 {model_config['name']} 失败: {e}")
    
    def _load_custom_models(self):
        """加载自定义模型配置"""
        if not self.custom_models_file.exists():
            # 创建空的自定义模型配置文件
            self.custom_models_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.custom_models_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            logger.info("创建了新的自定义模型配置文件")
            return
        
        try:
            with open(self.custom_models_file, 'r', encoding='utf-8') as f:
                custom_models = json.load(f)
            
            for model_id, model_data in custom_models.items():
                try:
                    # 验证模型配置
                    model_config = ModelConfig(**model_data)
                    
                    if model_config.enabled and model_config.api_key:
                        # 创建AI客户端
                        self.ai_clients[model_id] = openai.AsyncOpenAI(
                            api_key=model_config.api_key,
                            base_url=model_config.api_base
                        )
                        self._models_cache[model_id] = model_config.dict()
                        logger.info(f"成功加载自定义模型: {model_config.name}")
                    else:
                        logger.warning(f"自定义模型 {model_config.name} 未启用或缺少API密钥")
                        
                except Exception as e:
                    logger.error(f"加载自定义模型 {model_id} 失败: {e}")
                    
        except Exception as e:
            logger.error(f"读取自定义模型配置文件失败: {e}")
    
    def _save_custom_models(self):
        """保存自定义模型配置到文件"""
        try:
            custom_models = {}
            for model_id, model_config in self._models_cache.items():
                if model_config.get('type') == 'custom':
                    custom_models[model_id] = model_config
            
            with open(self.custom_models_file, 'w', encoding='utf-8') as f:
                json.dump(custom_models, f, ensure_ascii=False, indent=2)
            
            logger.info("自定义模型配置已保存")
            
        except Exception as e:
            logger.error(f"保存自定义模型配置失败: {e}")
            raise
    
    async def validate_model_config(self, model_config: ModelConfig) -> Dict[str, Any]:
        """
        验证模型配置是否有效
        
        Args:
            model_config: 模型配置
            
        Returns:
            验证结果
        """
        try:
            # 创建临时客户端进行测试
            test_client = openai.AsyncOpenAI(
                api_key=model_config.api_key,
                base_url=model_config.api_base
            )
            
            # 发送测试请求
            response = await test_client.chat.completions.create(
                model=model_config.model,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=10
            )
            
            return {
                "valid": True,
                "message": "模型配置验证成功",
                "test_response": response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"模型配置验证失败: {str(e)}",
                "error": str(e)
            }
    
    async def add_custom_model(self, model_id: str, model_config: ModelConfig) -> Dict[str, Any]:
        """
        添加自定义模型
        
        Args:
            model_id: 模型ID
            model_config: 模型配置
            
        Returns:
            添加结果
        """
        try:
            # 检查模型ID是否已存在
            if model_id in self._models_cache:
                return {
                    "success": False,
                    "message": f"模型ID '{model_id}' 已存在"
                }
            
            # 验证模型配置
            validation_result = await self.validate_model_config(model_config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": validation_result["message"]
                }
            
            # 添加到缓存
            model_config.type = "custom"
            self._models_cache[model_id] = model_config.dict()
            
            # 创建AI客户端
            if model_config.enabled and model_config.api_key:
                self.ai_clients[model_id] = openai.AsyncOpenAI(
                    api_key=model_config.api_key,
                    base_url=model_config.api_base
                )
            
            # 保存到文件
            self._save_custom_models()
            
            logger.info(f"成功添加自定义模型: {model_config.name}")
            
            return {
                "success": True,
                "message": f"自定义模型 '{model_config.name}' 添加成功",
                "model_id": model_id
            }
            
        except Exception as e:
            logger.error(f"添加自定义模型失败: {e}")
            return {
                "success": False,
                "message": f"添加失败: {str(e)}"
            }
    
    async def update_model(self, model_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新模型配置
        
        Args:
            model_id: 模型ID
            updates: 更新的配置项
            
        Returns:
            更新结果
        """
        try:
            if model_id not in self._models_cache:
                return {
                    "success": False,
                    "message": f"模型 '{model_id}' 不存在"
                }
            
            current_config = self._models_cache[model_id].copy()
            current_config.update(updates)
            
            # 验证更新后的配置
            model_config = ModelConfig(**current_config)
            
            # 如果是自定义模型，进行验证
            if current_config.get('type') == 'custom':
                validation_result = await self.validate_model_config(model_config)
                if not validation_result["valid"]:
                    return {
                        "success": False,
                        "message": validation_result["message"]
                    }
            
            # 更新缓存
            self._models_cache[model_id] = model_config.dict()
            
            # 更新AI客户端
            if model_config.enabled and model_config.api_key:
                self.ai_clients[model_id] = openai.AsyncOpenAI(
                    api_key=model_config.api_key,
                    base_url=model_config.api_base
                )
            elif model_id in self.ai_clients:
                del self.ai_clients[model_id]
            
            # 如果是自定义模型，保存到文件
            if current_config.get('type') == 'custom':
                self._save_custom_models()
            
            logger.info(f"成功更新模型: {model_config.name}")
            
            return {
                "success": True,
                "message": f"模型 '{model_config.name}' 更新成功"
            }
            
        except Exception as e:
            logger.error(f"更新模型失败: {e}")
            return {
                "success": False,
                "message": f"更新失败: {str(e)}"
            }
    
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        删除模型（仅限自定义模型）
        
        Args:
            model_id: 模型ID
            
        Returns:
            删除结果
        """
        try:
            if model_id not in self._models_cache:
                return {
                    "success": False,
                    "message": f"模型 '{model_id}' 不存在"
                }
            
            model_config = self._models_cache[model_id]
            
            # 只允许删除自定义模型
            if model_config.get('type') != 'custom':
                return {
                    "success": False,
                    "message": "只能删除自定义模型，内置模型无法删除"
                }
            
            # 从缓存中删除
            del self._models_cache[model_id]
            
            # 删除AI客户端
            if model_id in self.ai_clients:
                del self.ai_clients[model_id]
            
            # 保存到文件
            self._save_custom_models()
            
            logger.info(f"成功删除自定义模型: {model_config['name']}")
            
            return {
                "success": True,
                "message": f"自定义模型 '{model_config['name']}' 删除成功"
            }
            
        except Exception as e:
            logger.error(f"删除模型失败: {e}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有可用模型列表"""
        models = []
        for model_id, model_config in self._models_cache.items():
            if model_config.get('enabled', False):
                models.append({
                    "id": model_id,
                    "name": model_config.get('name', model_id),
                    "description": model_config.get('description', ''),
                    "supports_streaming": model_config.get('supports_streaming', False),
                    "max_tokens": model_config.get('max_tokens', 4000),
                    "type": model_config.get('type', 'unknown'),
                    "model": model_config.get('model', ''),
                    "api_base": model_config.get('api_base', ''),
                    "temperature": model_config.get('temperature', 0.7)
                })
        return models
    
    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的配置"""
        return self._models_cache.get(model_id)
    
    def get_ai_client(self, model_id: str = None):
        """获取指定模型的AI客户端"""
        if not model_id:
            model_id = self.config.DEFAULT_MODEL
        
        if model_id in self.ai_clients:
            return self.ai_clients[model_id], self._models_cache[model_id]
        else:
            # 回退到默认模型
            default_model = self.config.DEFAULT_MODEL
            if default_model in self.ai_clients:
                logger.warning(f"模型 {model_id} 不可用，使用默认模型 {default_model}")
                return self.ai_clients[default_model], self._models_cache[default_model]
            else:
                raise ValueError(f"没有可用的AI模型客户端")
    
    def refresh_models(self):
        """刷新模型配置（重新加载）"""
        logger.info("刷新模型配置...")
        self.ai_clients.clear()
        self._models_cache.clear()
        self._init_builtin_models()
        self._load_custom_models()
        logger.info("模型配置刷新完成") 