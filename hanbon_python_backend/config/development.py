#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: development.py
@description: 开发环境配置
@author: AI Assistant
@created: 2024
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DevelopmentConfig:
    """开发环境配置类"""
    
    # 基础配置
    DEBUG = True
    TESTING = False
    
    # API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    OPENMEMORY_API_KEY = os.getenv('OPENMEMORY_API_KEY', '')
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', '')
    BING_API_KEY = os.getenv('BING_API_KEY', '')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    
    # AI模型配置
    AI_MODELS = {
        'deepseek': {
            'name': 'DeepSeek',
            'model': 'deepseek-chat',
            'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'api_base': os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
            'max_tokens': int(os.getenv('DEEPSEEK_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': '专业的中文对话模型',
            'enabled': True,
            'type': 'builtin'  # 内置模型
        },
        'deepseek_huoshan': {
            'name': 'DeepSeek_huoshan',
            'model': 'deepseek-v3-250324',
            'api_key': os.getenv('DEEPSEEK_HUOSHAN_API_KEY', ''),
            'api_base': os.getenv('DEEPSEEK_HUOSHAN_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3'),
            'max_tokens': int(os.getenv('DEEPSEEK_HUOSHAN_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('DEEPSEEK_HUOSHAN_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': '专业的中文对话模型',
            'enabled': True,
            'type': 'builtin'  # 内置模型
        },
        'doubao_huoshan': {
            'name': 'Doubao_huoshan',
            'model': 'doubao-seed-1-6-250615',
            'api_key': os.getenv('DEEPSEEK_HUOSHAN_API_KEY', ''),
            'api_base': os.getenv('DOUBAO_HUOSHAN_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3'),
            'max_tokens': int(os.getenv('DOUBAO_HUOSHAN_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('DOUBAN1_HUOSHAN_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': '专业的中文对话模型',
            'enabled': True,
            'type': 'builtin'  # 内置模型
        },
        'qwen': {
            'name': 'Qwen',
            'model': 'qwen-max',
            'api_key': os.getenv('QWEN_API_KEY', ''),
            'api_base': os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
            'max_tokens': int(os.getenv('QWEN_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('QWEN_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': '阿里云通义千问大模型',
            'enabled': bool(os.getenv('QWEN_API_KEY', '')),
            'type': 'builtin'
        },
        'chatgpt_4.1': {
            'name': 'ChatGPT',
            'model': 'gpt-4.1-nano',
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': 'OpenAI GPT-4.1-nano',
            'enabled': bool(os.getenv('OPENAI_API_KEY', '')),
            'type': 'builtin'
        },
        'chatgpt': {
            'name': 'ChatGPT',
            'model': 'gpt-3.5-turbo',
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': 'OpenAI GPT-3.5 Turbo',
            'enabled': bool(os.getenv('OPENAI_API_KEY', '')),
            'type': 'builtin'
        },
        'gpt4': {
            'name': 'GPT-4',
            'model': 'gpt-4',
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'max_tokens': int(os.getenv('GPT4_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('GPT4_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': 'OpenAI GPT-4 高级模型',
            'enabled': bool(os.getenv('OPENAI_API_KEY', '')),
            'type': 'builtin'
        },
        'claude': {
            'name': 'Claude',
            'model': 'claude-3-sonnet-20240229',
            'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
            'api_base': os.getenv('ANTHROPIC_API_BASE', 'https://api.anthropic.com'),
            'max_tokens': int(os.getenv('CLAUDE_MAX_TOKENS', '16384')),
            'temperature': float(os.getenv('CLAUDE_TEMPERATURE', '0.7')),
            'supports_streaming': True,
            'description': 'Anthropic Claude 3 Sonnet',
            'enabled': bool(os.getenv('ANTHROPIC_API_KEY', '')),
            'type': 'builtin'
        }
    }
    
    # 自定义模型配置存储路径
    CUSTOM_MODELS_CONFIG_PATH = os.getenv('CUSTOM_MODELS_CONFIG_PATH', 'config/custom_models.json')
    
    # 模型配置验证规则
    MODEL_CONFIG_SCHEMA = {
        'required_fields': ['name', 'model', 'api_key', 'api_base'],
        'optional_fields': ['max_tokens', 'temperature', 'supports_streaming', 'description', 'enabled'],
        'defaults': {
            'max_tokens': 4000,
            'temperature': 0.7,
            'supports_streaming': True,
            'description': '',
            'enabled': True,
            'type': 'custom'
        }
    }
    
    # 默认模型
    DEFAULT_MODEL = os.getenv('DEFAULT_AI_MODEL', 'deepseek')
    
    # 兼容性配置（保持向后兼容）
    DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '4000'))
    DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
    
    # OpenMemory配置
    OPENMEMORY_BASE_URL = os.getenv('OPENMEMORY_BASE_URL', 'https://api.openmemory.ai')
    OPENMEMORY_MAX_MEMORIES = int(os.getenv('OPENMEMORY_MAX_MEMORIES', '100'))
    
    # Redis配置（用于缓存）
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///hanbon_agent.db')
    
    # 高德地图配置
    AMAP_BASE_URL = 'https://restapi.amap.com/v3'
    
    # Bing搜索配置
    BING_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/search'
    BING_IMAGE_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/images/search'
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/hanbon_agent.log'
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080']
    
    # Session配置
    SESSION_TIMEOUT = 3600  # 1小时
    
    # MCP工具配置
    MCP_TOOLS = {
        'amap_search': {
            'enabled': True,
            'api_key': AMAP_API_KEY
        },
        'bing_search': {
            'enabled': True,
            'api_key': BING_API_KEY
        },
        'weather_api': {
            'enabled': True,
            'api_key': OPENWEATHER_API_KEY
        },
        'food_recommendation': {
            'enabled': True
        },
        'image_search': {
            'enabled': True,
            'api_key': BING_API_KEY
        },
        'recipe_generator': {
            'enabled': True
        }
    }
    
    # AI Agent配置
    AGENT_CONFIG = {
        'max_conversation_length': 50,
        'memory_retention_days': 30,
        'enable_function_calling': True,
        'enable_streaming': True,
        'default_personality': 'friendly_food_expert'
    }
    
    @classmethod
    def validate_config(cls):
        """验证配置是否完整"""
        required_keys = ['DEEPSEEK_API_KEY']
        missing_keys = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing_keys)}")
        
        return True 