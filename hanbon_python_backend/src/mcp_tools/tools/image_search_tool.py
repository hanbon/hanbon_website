#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: image_search_tool.py
@description: Bing图片搜索工具 - 基于爬虫的真实搜索
@author: AI Assistant  
@created: 2024
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from urllib import parse
from bs4 import BeautifulSoup
from pydantic import BaseModel
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class ImageResult(BaseModel):
    """图片搜索结果模型"""
    url: str
    title: str
    source: str

class ImageSearchTool(BaseMCPTool):
    """Bing图片搜索工具"""
    
    def __init__(self, name: str, description: str, **config):
        super().__init__(name, description, **config)
        self.category = "search"
        self.bing_path = 'https://cn.bing.com/images/search'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
        }
        
    async def execute(self, **parameters) -> Dict[str, Any]:
        """
        执行图片搜索
        
        Args:
            query: 搜索关键词
            count: 图片数量，默认10
            
        Returns:
            搜索结果
        """
        try:
            query = parameters.get('query', '')
            count = parameters.get('count', 10)
            
            if not query.strip():
                return {
                    "success": False,
                    "error": "搜索关键词不能为空",
                    "images": []
                }
            
            # 执行Bing图片搜索
            images = await self._bing_crawler(query, count)
            
            if images:
                return {
                    "success": True,
                    "query": query,
                    "count": len(images),
                    "images": [img.dict() for img in images],
                    "message": f"成功找到 {len(images)} 张关于'{query}'的图片"
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "count": 0,
                    "images": [],
                    "message": f"未找到关于'{query}'的图片"
                }
                
        except Exception as e:
            logger.error(f"图片搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": [],
                "message": "图片搜索过程中发生错误"
            }
    
    async def _bing_crawler(self, key_word: str, image_num: int) -> Optional[List[ImageResult]]:
        """
        Bing图片爬虫核心方法
        
        Args:
            key_word: 搜索关键词
            image_num: 需要的图片数量
            
        Returns:
            图片搜索结果列表或None
        """
        try:
            # 构建搜索URL
            query_params = {
                'q': key_word,
                'count': min(image_num * 2, 50),  # 多获取一些以防解析失败
                'form': 'HDRSC2',
                'first': 1
            }
            
            url = self.bing_path + '?' + parse.urlencode(query_params)
            logger.info(f"开始搜索图片: {key_word}, URL: {url}")
            
            # 异步请求
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Bing请求失败: {response.status}")
                        return None
                    
                    html_content = await response.text()
            
            # 解析HTML
            soup = BeautifulSoup(html_content, "html.parser")
            results = []
            
            # 查找图片容器
            image_containers = soup.select('.iusc')
            
            if not image_containers:
                logger.warning(f"未找到图片容器，可能页面结构已变化")
                # 尝试其他选择器
                image_containers = soup.select('[data-src]') or soup.select('img[src]')
            
            for container in image_containers:
                try:
                    # 尝试多种方式提取图片URL
                    img_url = self._extract_image_url(container)
                    title = self._extract_image_title(container)
                    
                    if img_url and self._is_valid_image_url(img_url):
                        results.append(ImageResult(
                            url=img_url,
                            title=title or f"{key_word}相关图片",
                            source="bing"
                        ))
                        
                        if len(results) >= image_num:
                            break
                            
                except Exception as e:
                    logger.debug(f"解析单个图片失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(results)} 张图片")
            return results if results else None
            
        except Exception as e:
            logger.error(f"Bing图片爬虫失败: {e}")
            return None
    
    def _extract_image_url(self, container) -> Optional[str]:
        """从容器中提取图片URL"""
        try:
            # 方法1: 从href中解析
            if container.get('href'):
                href = container.get('href')
                decoded_href = parse.unquote(href)
                
                # 查找mediaurl参数
                if 'mediaurl=' in decoded_href:
                    parts = decoded_href.split('mediaurl=')
                    if len(parts) > 1:
                        media_url = parts[1].split('&')[0]
                        return media_url
            
            # 方法2: 从data-src属性提取  
            if container.get('data-src'):
                return container.get('data-src')
            
            # 方法3: 从src属性提取
            if container.get('src'):
                return container.get('src')
            
            # 方法4: 查找子元素img标签
            img_tag = container.find('img')
            if img_tag:
                return img_tag.get('src') or img_tag.get('data-src')
                
        except Exception as e:
            logger.debug(f"提取图片URL失败: {e}")
            
        return None
    
    def _extract_image_title(self, container) -> str:
        """提取图片标题"""
        try:
            # 尝试多种方式获取标题
            title = (
                container.get('alt') or 
                container.get('title') or 
                container.get('aria-label') or
                ""
            )
            
            # 如果容器没有标题，尝试查找子元素
            if not title:
                img_tag = container.find('img')
                if img_tag:
                    title = img_tag.get('alt') or img_tag.get('title') or ""
            
            return title.strip()
            
        except Exception:
            return ""
    
    def _is_valid_image_url(self, url: str) -> bool:
        """验证是否为有效的图片URL"""
        if not url or len(url) < 10:
            return False
        
        # 检查是否包含图片文件扩展名或图片相关参数
        image_indicators = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            'images/', '/image/', 'photo', 'pic'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in image_indicators)
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "图片搜索关键词，如'红烧肉'、'川菜'等"
                },
                "count": {
                    "type": "integer",
                    "description": "需要搜索的图片数量",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["query"]
        }
    
    async def search_food_images(self, food_name: str, count: int = 10) -> Dict[str, Any]:
        """
        搜索美食图片的便捷方法
        
        Args:
            food_name: 美食名称
            count: 图片数量
            
        Returns:
            搜索结果
        """
        return await self.execute(query=food_name, count=count)
    
    async def search_recipe_images(self, recipe_name: str, count: int = 5) -> Dict[str, Any]:
        """
        搜索菜谱图片的便捷方法
        
        Args:
            recipe_name: 菜谱名称
            count: 图片数量
            
        Returns:
            搜索结果
        """
        query = f"{recipe_name} 制作过程 菜谱"
        return await self.execute(query=query, count=count) 