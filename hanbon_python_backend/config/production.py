#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: production.py
@description: 生产环境配置
@author: AI Assistant
@created: 2024
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ProductionConfig:
    """生产环境配置类"""
    
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENMEMORY_API_KEY = os.getenv('OPENMEMORY_API_KEY')
    AMAP_API_KEY = os.getenv('AMAP_API_KEY')
    BING_API_KEY = os.getenv('BING_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # DeepSeek配置
    DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '4000'))
    DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3'))
    
    # OpenMemory配置
    OPENMEMORY_BASE_URL = os.getenv('OPENMEMORY_BASE_URL', 'https://api.openmemory.ai')
    OPENMEMORY_MAX_MEMORIES = int(os.getenv('OPENMEMORY_MAX_MEMORIES', '1000'))
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # 高德地图配置
    AMAP_BASE_URL = 'https://restapi.amap.com/v3'
    
    # Bing搜索配置
    BING_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/search'
    BING_IMAGE_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/images/search'
    
    # 文件上传配置
    UPLOAD_FOLDER = '/var/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 日志配置
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/hanbon_agent.log'
    
    # CORS配置
    CORS_ORIGINS = [
        'https://hanbon.xyz',
        'https://www.hanbon.xyz'
    ]
    
    # Session配置
    SESSION_TIMEOUT = 7200  # 2小时
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY')
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
    
    # MCP工具配置
    MCP_TOOLS = {
        'amap_search': {
            'enabled': True,
            'api_key': AMAP_API_KEY,
            'rate_limit': 1000  # 每小时请求限制
        },
        'bing_search': {
            'enabled': True,
            'api_key': BING_API_KEY,
            'rate_limit': 3000
        },
        'weather_api': {
            'enabled': True,
            'api_key': OPENWEATHER_API_KEY,
            'rate_limit': 1000
        },
        'food_recommendation': {
            'enabled': True,
            'rate_limit': 5000
        },
        'image_search': {
            'enabled': True,
            'api_key': BING_API_KEY,
            'rate_limit': 1000
        },
        'recipe_generator': {
            'enabled': True,
            'rate_limit': 2000
        }
    }
    
    # AI Agent配置
    AGENT_CONFIG = {
        'max_conversation_length': 100,
        'memory_retention_days': 90,
        'enable_function_calling': True,
        'enable_streaming': True,
        'default_personality': 'professional_food_expert',
        'rate_limit_per_user': 100  # 每小时每用户限制
    }
    
    # 监控配置
    MONITORING = {
        'enable_metrics': True,
        'metrics_port': 9090,
        'health_check_interval': 30
    }
    
    @classmethod
    def validate_config(cls):
        """验证生产环境配置"""
        required_keys = [
            'DEEPSEEK_API_KEY',
            'DATABASE_URL',
            'SECRET_KEY'
        ]
        missing_keys = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"生产环境缺少必需的配置项: {', '.join(missing_keys)}")
        
        return True 