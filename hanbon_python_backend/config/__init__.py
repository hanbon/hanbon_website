#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: __init__.py
@description: 配置模块初始化
@author: AI Assistant
@created: 2024
"""

from .development import DevelopmentConfig
from .production import ProductionConfig
import os

def get_config():
    """根据环境变量获取配置"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

__all__ = ['get_config', 'DevelopmentConfig', 'ProductionConfig'] 