#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: bing_search_tool.py  
@description: 必应搜索工具
@author: AI Assistant
@created: 2024
"""

import aiohttp
import logging
from typing import Dict, Any
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class BingSearchTool(BaseMCPTool):
    """必应搜索工具"""
    
    def __init__(self, name: str, description: str, api_key: str, **config):
        super().__init__(name, description, **config)
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.category = "search"
        
    async def execute(self, **parameters) -> Dict[str, Any]:
        """执行搜索"""
        try:
            query = parameters.get('query', '')
            count = parameters.get('count', 5)
            
            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            params = {'q': query, 'count': count, 'responseFilter': 'Webpages'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
                    else:
                        return {"error": f"搜索失败: {response.status}", "results": []}
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"error": str(e), "results": []}
    
    def _parse_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析搜索结果"""
        webpages = data.get('webPages', {}).get('value', [])
        results = []
        
        for page in webpages:
            results.append({
                "title": page.get('name', ''),
                "url": page.get('url', ''),
                "snippet": page.get('snippet', ''),
                "date": page.get('dateLastCrawled', '')
            })
        
        return {"success": True, "results": results}
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索查询"},
                "count": {"type": "integer", "description": "结果数量", "default": 5}
            },
            "required": ["query"]
        } 