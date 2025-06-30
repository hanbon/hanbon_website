#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: mcp_manager.py
@description: MCP工具管理器
@author: AI Assistant
@created: 2024
"""

import asyncio
import logging
from typing import Dict, List, Any

# 导入基类
from .base_tool import BaseMCPTool, ToolMetadata

# 导入具体的工具实现
from .tools.amap_tool import AmapTool
from .tools.bing_search_tool import BingSearchTool
from .tools.weather_tool import WeatherTool
from .tools.food_recommendation_tool import FoodRecommendationTool
from .tools.image_search_tool import ImageSearchTool
from .tools.recipe_generator_tool import RecipeGeneratorTool

logger = logging.getLogger(__name__)

class MCPToolManager:
    """MCP工具管理器"""
    
    def __init__(self, model_manager=None):
        """初始化MCP工具管理器
        
        Args:
            model_manager: 模型管理器实例
        """
        self.tools: Dict[str, BaseMCPTool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.execution_count: Dict[str, int] = {}
        self.last_execution: Dict[str, float] = {}
        self.model_manager = model_manager
        
    async def initialize(self):
        """初始化所有工具"""
        try:
            logger.info("正在初始化MCP工具...")
            
            # 注册所有可用工具
            await self._register_tools()
            
            logger.info(f"成功初始化 {len(self.tools)} 个MCP工具")
            
        except Exception as e:
            logger.error(f"MCP工具初始化失败: {e}")
            raise
    
    async def _register_tools(self):
        """注册所有工具"""
        # 高德地图工具
        amap_tool = AmapTool(
            name="amap_search",
            description="高德地图搜索工具，用于查找餐厅、美食地点等",
            api_key=self._get_config_value('AMAP_API_KEY')
        )
        await self._register_tool(amap_tool)
        
        # 必应搜索工具
        bing_tool = BingSearchTool(
            name="bing_search",
            description="必应搜索工具，用于获取最新的网络信息",
            api_key=self._get_config_value('BING_API_KEY')
        )
        await self._register_tool(bing_tool)
        
        # 天气API工具 (使用OpenWeather API)
        weather_tool = WeatherTool(
            name="weather_api",
            description="天气API工具，用于获取天气信息和基于天气的美食推荐",
            api_key=self._get_config_value('OPENWEATHER_API_KEY')
        )
        await self._register_tool(weather_tool)
        
        # 美食推荐工具
        food_rec_tool = FoodRecommendationTool(
            name="food_recommendation",
            description="智能美食推荐工具，基于用户偏好推荐美食"
        )
        await self._register_tool(food_rec_tool)
        
        # 图片搜索工具（基于Bing爬虫）
        image_tool = ImageSearchTool(
            name="image_search",
            description="Bing图片搜索工具，用于搜索美食相关图片（基于爬虫技术）"
        )
        await self._register_tool(image_tool)
        
        # 菜谱生成工具
        recipe_tool = RecipeGeneratorTool(
            name="recipe_generator",
            description="AI菜谱生成工具，使用用户选择的默认模型生成详细的烹饪菜谱",
            model_manager=self.model_manager
        )
        await self._register_tool(recipe_tool)
    
    def _get_config_value(self, key: str, default: str = "") -> str:
        """获取配置值"""
        import os
        return os.getenv(key, default)
    
    async def _register_tool(self, tool: BaseMCPTool):
        """注册单个工具"""
        try:
            # 验证工具
            if not tool.name:
                raise ValueError("工具名称不能为空")
            
            # 注册工具
            self.tools[tool.name] = tool
            self.tool_metadata[tool.name] = tool.get_metadata()
            self.execution_count[tool.name] = 0
            
            logger.info(f"成功注册工具: {tool.name}")
            
        except Exception as e:
            logger.error(f"注册工具 {tool.name} 失败: {e}")
            raise
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行指定工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            执行结果
        """
        import time
        start_time = time.time()
        
        # 记录工具调用输入日志
        logger.info(f"🔧 MCP工具调用开始")
        logger.info(f"   工具名称: {tool_name}")
        logger.info(f"   输入参数: {parameters}")
        
        try:
            # 检查工具是否存在
            if tool_name not in self.tools:
                error_msg = f"工具 '{tool_name}' 不存在"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            tool = self.tools[tool_name]
            
            # 检查工具是否启用
            if not tool.enabled:
                error_msg = f"工具 '{tool_name}' 已禁用"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # 检查速率限制
            if not self._check_rate_limit(tool_name):
                error_msg = f"工具 '{tool_name}' 达到速率限制"
                logger.error(f"⚠️ {error_msg}")
                raise ValueError(error_msg)
            
            # 验证参数
            logger.info(f"📋 验证工具参数...")
            self._validate_parameters(tool, parameters)
            
            # 执行工具
            logger.info(f"⚙️ 开始执行工具: {tool_name}")
            result = await tool.execute(**parameters)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 记录工具调用输出日志
            logger.info(f"✅ MCP工具调用成功")
            logger.info(f"   工具名称: {tool_name}")
            logger.info(f"   执行时间: {execution_time:.2f}秒")
            logger.info(f"   输出结果: {result}")
            
            # 更新执行统计
            self._update_execution_stats(tool_name)
            
            final_result = {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_time": execution_time
            }
            
            logger.info(f"📤 最终返回结果: {final_result}")
            return final_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
                "execution_time": execution_time
            }
            
            logger.error(f"❌ MCP工具调用失败")
            logger.error(f"   工具名称: {tool_name}")
            logger.error(f"   执行时间: {execution_time:.2f}秒")
            logger.error(f"   错误信息: {str(e)}")
            logger.error(f"   错误结果: {error_result}")
            
            return error_result
    
    def _check_rate_limit(self, tool_name: str) -> bool:
        """检查速率限制"""
        tool = self.tools[tool_name]
        if not tool.rate_limit:
            return True
        
        import time
        current_time = time.time()
        last_exec = self.last_execution.get(tool_name, 0)
        
        # 简单的速率限制检查（每分钟最大调用次数）
        if current_time - last_exec < 60:
            if self.execution_count.get(tool_name, 0) >= tool.rate_limit:
                return False
        else:
            # 重置计数器
            self.execution_count[tool_name] = 0
        
        return True
    
    def _validate_parameters(self, tool: BaseMCPTool, parameters: Dict[str, Any]):
        """验证工具参数"""
        schema = tool.get_parameters_schema()
        required_params = schema.get('required', [])
        
        # 检查必需参数
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"缺少必需参数: {param}")
        
        # 可以添加更多参数验证逻辑
    
    def _update_execution_stats(self, tool_name: str):
        """更新执行统计"""
        import time
        self.execution_count[tool_name] = self.execution_count.get(tool_name, 0) + 1
        self.last_execution[tool_name] = time.time()
    
    def _get_execution_time(self) -> float:
        """获取执行时间（占位符）"""
        import time
        return time.time()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        tools_info = []
        
        for tool_name, metadata in self.tool_metadata.items():
            tools_info.append({
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "enabled": metadata.enabled,
                "parameters": metadata.parameters,
                "execution_count": self.execution_count.get(tool_name, 0)
            })
        
        return tools_info
    
    async def enable_tool(self, tool_name: str):
        """启用工具"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = True
            self.tool_metadata[tool_name].enabled = True
            logger.info(f"已启用工具: {tool_name}")
        else:
            raise ValueError(f"工具 '{tool_name}' 不存在")
    
    async def disable_tool(self, tool_name: str):
        """禁用工具"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = False
            self.tool_metadata[tool_name].enabled = False
            logger.info(f"已禁用工具: {tool_name}")
        else:
            raise ValueError(f"工具 '{tool_name}' 不存在")
    
    async def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """获取工具状态"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        metadata = self.tool_metadata[tool_name]
        
        return {
            "name": metadata.name,
            "description": metadata.description,
            "enabled": metadata.enabled,
            "execution_count": self.execution_count.get(tool_name, 0),
            "last_execution": self.last_execution.get(tool_name, None),
            "rate_limit": metadata.rate_limit
        }
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理MCP工具资源...")
        
        # 清理各个工具的资源
        for tool in self.tools.values():
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception as e:
                    logger.warning(f"清理工具 {tool.name} 资源失败: {e}")
        
        # 清理管理器状态
        self.tools.clear()
        self.tool_metadata.clear()
        self.execution_count.clear()
        self.last_execution.clear()
        
        logger.info("MCP工具资源清理完成")
    
    @property
    def available_tools(self) -> List[str]:
        """获取可用工具名称列表"""
        return [name for name, tool in self.tools.items() if tool.enabled]
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """按类别获取工具"""
        return [
            name for name, metadata in self.tool_metadata.items()
            if metadata.category == category and metadata.enabled
        ]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        total_executions = sum(self.execution_count.values())
        
        return {
            "total_tools": len(self.tools),
            "enabled_tools": len(self.available_tools),
            "total_executions": total_executions,
            "tool_stats": {
                name: {
                    "executions": count,
                    "last_execution": self.last_execution.get(name)
                }
                for name, count in self.execution_count.items()
            }
        } 