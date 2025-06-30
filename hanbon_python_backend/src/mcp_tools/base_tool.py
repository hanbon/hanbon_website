#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: base_tool.py
@description: MCP工具基类定义
@author: AI Assistant
@created: 2024
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolMetadata:
    """工具元数据"""
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str
    enabled: bool = True
    rate_limit: Optional[int] = None

class BaseMCPTool(ABC):
    """MCP工具基类"""
    
    def __init__(self, name: str, description: str, **config):
        self.name = name
        self.description = description
        self.config = config
        self.enabled = config.get('enabled', True)
        self.rate_limit = config.get('rate_limit', None)
    
    @abstractmethod
    async def execute(self, **parameters) -> Dict[str, Any]:
        """执行工具功能"""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        pass
    
    def get_metadata(self) -> ToolMetadata:
        """获取工具元数据"""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters_schema(),
            category=getattr(self, 'category', 'general'),
            enabled=self.enabled,
            rate_limit=self.rate_limit
        ) 