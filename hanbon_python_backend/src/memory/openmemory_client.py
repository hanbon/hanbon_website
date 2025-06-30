#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: openmemory_client.py
@description: OpenMemory客户端实现
@author: AI Assistant
@created: 2024
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Memory:
    """记忆数据结构"""
    id: str
    user_id: str
    content: Dict[str, Any]
    memory_type: str
    timestamp: datetime
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None

class OpenMemoryClient:
    """OpenMemory API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openmemory.ai"):
        """
        初始化OpenMemory客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 本地缓存（生产环境中应使用Redis等外部缓存）
        self.local_cache: Dict[str, List[Memory]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
    async def initialize(self):
        """初始化客户端连接"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'HanbonFoodAgent/1.0'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # 测试连接
            try:
                connection_ok = await self._test_connection()
                if connection_ok:
                    logger.info("OpenMemory客户端初始化成功，API连接正常")
                else:
                    logger.warning("OpenMemory API连接失败，将使用本地缓存模式")
                    await self.session.close()
                    self.session = None
            except Exception as conn_error:
                logger.warning(f"OpenMemory连接测试失败: {conn_error}")
                logger.info("切换到本地缓存模式")
                await self.session.close()
                self.session = None
            
        except Exception as e:
            logger.warning(f"OpenMemory客户端初始化失败，使用本地缓存模式: {e}")
            # 在无法创建session时，使用本地内存作为回退
            self.session = None
        
        # 无论是否连接到API，都确保本地缓存可用
        if not hasattr(self, 'local_cache'):
            self.local_cache = {}
            self.cache_expiry = {}
        
        logger.info("记忆客户端初始化完成（本地缓存已就绪）")

    async def close(self):
        """关闭客户端连接"""
        if self.session:
            await self.session.close()

    async def _test_connection(self):
        """测试API连接"""
        if not self.session:
            return False
            
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    # 检查响应内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/json' in content_type:
                        try:
                            data = await response.json()
                            logger.info("API健康检查通过")
                            return True
                        except json.JSONDecodeError:
                            logger.warning("健康检查返回非JSON格式，但状态码为200，假设连接正常")
                            return True
                    else:
                        logger.warning(f"健康检查返回非JSON格式: {content_type}")
                        if 'text/html' in content_type:
                            response_text = await response.text()
                            logger.error(f"健康检查返回HTML页面。响应前200字符: {response_text[:200]}")
                        return False
                else:
                    logger.warning(f"健康检查失败: HTTP {response.status}")
                    return False
        except aiohttp.ClientError as e:
            logger.error(f"健康检查网络异常: {e}")
            raise Exception(f"连接测试失败: {e}")
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
            raise Exception(f"连接测试失败: {e}")

    async def add_memory(
        self, 
        user_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str = "conversation"
    ) -> bool:
        """
        添加新记忆
        
        Args:
            user_id: 用户ID
            memory_data: 记忆数据
            memory_type: 记忆类型
            
        Returns:
            是否成功添加
        """
        try:
            memory = Memory(
                id=f"{user_id}_{datetime.now().isoformat()}",
                user_id=user_id,
                content=memory_data,
                memory_type=memory_type,
                timestamp=datetime.now(),
                metadata={"created_by": "food_agent"}
            )
            
            # 尝试通过API添加
            if self.session:
                success = await self._add_memory_via_api(memory)
                if success:
                    # 同时更新本地缓存
                    self._add_to_local_cache(memory)
                    return True
            
            # API失败时使用本地缓存
            self._add_to_local_cache(memory)
            return True
            
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            return False

    async def _add_memory_via_api(self, memory: Memory) -> bool:
        """通过API添加记忆"""
        try:
            payload = {
                "user_id": memory.user_id,
                "content": memory.content,
                "type": memory.memory_type,
                "timestamp": memory.timestamp.isoformat(),
                "metadata": memory.metadata
            }
            
            async with self.session.post(
                f"{self.base_url}/memories",
                json=payload
            ) as response:
                if response.status == 201:
                    logger.info(f"成功通过API添加记忆: {memory.id}")
                    return True
                else:
                    logger.warning(f"API添加记忆失败: HTTP {response.status}")
                    # 记录响应内容以便调试
                    try:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'text/html' in content_type:
                            response_text = await response.text()
                            logger.error(f"API返回HTML页面。响应前200字符: {response_text[:200]}")
                        else:
                            response_text = await response.text()
                            logger.debug(f"失败响应内容: {response_text[:200]}")
                    except:
                        pass
                    return False
                    
        except aiohttp.ClientError as e:
            logger.error(f"API网络请求异常: {e}")
            return False
        except Exception as e:
            logger.error(f"API添加记忆异常: {e}")
            return False

    def _add_to_local_cache(self, memory: Memory):
        """添加到本地缓存"""
        if memory.user_id not in self.local_cache:
            self.local_cache[memory.user_id] = []
        
        self.local_cache[memory.user_id].append(memory)
        
        # 限制每个用户的记忆数量（最多保留100条）
        if len(self.local_cache[memory.user_id]) > 100:
            self.local_cache[memory.user_id] = self.local_cache[memory.user_id][-100:]
        
        # 更新缓存过期时间
        self.cache_expiry[memory.user_id] = datetime.now() + timedelta(hours=1)

    async def get_user_memories(
        self, 
        user_id: str, 
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取用户记忆
        
        Args:
            user_id: 用户ID
            memory_type: 记忆类型过滤
            limit: 返回数量限制
            
        Returns:
            用户记忆列表
        """
        try:
            # 首先尝试从API获取
            if self.session:
                api_memories = await self._get_memories_via_api(user_id, memory_type, limit)
                if api_memories:
                    return api_memories
            
            # API失败时使用本地缓存
            return self._get_from_local_cache(user_id, memory_type, limit)
            
        except Exception as e:
            logger.error(f"获取用户记忆失败: {e}")
            return []

    async def _get_memories_via_api(
        self, 
        user_id: str, 
        memory_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """通过API获取记忆"""
        try:
            params = {
                "user_id": user_id,
                "limit": limit
            }
            if memory_type:
                params["type"] = memory_type
            
            async with self.session.get(
                f"{self.base_url}/memories",
                params=params
            ) as response:
                if response.status == 200:
                    # 检查响应内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/json' not in content_type:
                        logger.warning(f"API返回非JSON格式响应，Content-Type: {content_type}")
                        if 'text/html' in content_type:
                            response_text = await response.text()
                            logger.error(f"API返回HTML页面，可能是认证失败或端点不存在。响应前200字符: {response_text[:200]}")
                        return []
                    
                    try:
                        data = await response.json()
                        logger.info(f"成功通过API获取记忆: {len(data)} 条")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {e}")
                        return []
                else:
                    logger.warning(f"API获取记忆失败: HTTP {response.status}")
                    # 记录响应内容以便调试
                    try:
                        response_text = await response.text()
                        logger.debug(f"失败响应内容: {response_text[:200]}")
                    except:
                        pass
                    return []
                    
        except aiohttp.ClientError as e:
            logger.error(f"API网络请求异常: {e}")
            return []
        except Exception as e:
            logger.error(f"API获取记忆异常: {e}")
            return []

    def _get_from_local_cache(
        self, 
        user_id: str, 
        memory_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """从本地缓存获取记忆"""
        if user_id not in self.local_cache:
            return []
        
        memories = self.local_cache[user_id]
        
        # 按类型过滤
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        # 按时间排序（最新的在前）
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        
        # 限制数量
        memories = memories[:limit]
        
        # 转换为字典格式
        return [
            {
                "id": m.id,
                "user_id": m.user_id,
                "content": m.content,
                "type": m.memory_type,
                "timestamp": m.timestamp.isoformat(),
                "metadata": m.metadata
            }
            for m in memories
        ]

    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索相关记忆
        
        Args:
            user_id: 用户ID
            query: 搜索查询
            limit: 返回数量限制
            
        Returns:
            相关记忆列表
        """
        try:
            # 首先尝试通过API搜索
            if self.session:
                api_results = await self._search_memories_via_api(user_id, query, limit)
                if api_results:
                    return api_results
            
            # API失败时使用本地搜索
            return self._search_local_cache(user_id, query, limit)
            
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []

    async def _search_memories_via_api(
        self, 
        user_id: str, 
        query: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """通过API搜索记忆"""
        try:
            payload = {
                "user_id": user_id,
                "query": query,
                "limit": limit
            }
            
            async with self.session.post(
                f"{self.base_url}/memories/search",
                json=payload
            ) as response:
                if response.status == 200:
                    # 检查响应内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/json' not in content_type:
                        logger.warning(f"API搜索返回非JSON格式响应，Content-Type: {content_type}")
                        if 'text/html' in content_type:
                            response_text = await response.text()
                            logger.error(f"API返回HTML页面，可能是认证失败或端点不存在。响应前200字符: {response_text[:200]}")
                        return []
                    
                    try:
                        data = await response.json()
                        logger.info(f"API搜索返回 {len(data)} 条记忆")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {e}")
                        return []
                else:
                    logger.warning(f"API搜索失败: HTTP {response.status}")
                    # 记录响应内容以便调试
                    try:
                        response_text = await response.text()
                        logger.debug(f"失败响应内容: {response_text[:200]}")
                    except:
                        pass
                    return []
                    
        except aiohttp.ClientError as e:
            logger.error(f"API网络请求异常: {e}")
            return []
        except Exception as e:
            logger.error(f"API搜索异常: {e}")
            return []

    def _search_local_cache(
        self, 
        user_id: str, 
        query: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """在本地缓存中搜索记忆"""
        if user_id not in self.local_cache:
            return []
        
        query_lower = query.lower()
        scored_memories = []
        
        for memory in self.local_cache[user_id]:
            score = 0
            
            # 在记忆内容中搜索关键词
            content_str = json.dumps(memory.content, ensure_ascii=False).lower()
            if query_lower in content_str:
                score += 1
            
            # 计算关键词匹配度
            query_words = query_lower.split()
            for word in query_words:
                if word in content_str:
                    score += 0.5
            
            if score > 0:
                scored_memories.append((memory, score))
        
        # 按相关性排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个结果
        results = []
        for memory, score in scored_memories[:limit]:
            results.append({
                "id": memory.id,
                "user_id": memory.user_id,
                "content": memory.content,
                "type": memory.memory_type,
                "timestamp": memory.timestamp.isoformat(),
                "relevance_score": score,
                "metadata": memory.metadata
            })
        
        return results

    async def update_memory(
        self, 
        memory_id: str, 
        updated_content: Dict[str, Any]
    ) -> bool:
        """
        更新记忆内容
        
        Args:
            memory_id: 记忆ID
            updated_content: 更新的内容
            
        Returns:
            是否成功更新
        """
        try:
            # 尝试通过API更新
            if self.session:
                success = await self._update_memory_via_api(memory_id, updated_content)
                if success:
                    return True
            
            # API失败时更新本地缓存
            return self._update_local_cache(memory_id, updated_content)
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False

    async def _update_memory_via_api(
        self, 
        memory_id: str, 
        updated_content: Dict[str, Any]
    ) -> bool:
        """通过API更新记忆"""
        try:
            payload = {
                "content": updated_content,
                "updated_at": datetime.now().isoformat()
            }
            
            async with self.session.put(
                f"{self.base_url}/memories/{memory_id}",
                json=payload
            ) as response:
                if response.status == 200:
                    logger.info(f"成功通过API更新记忆: {memory_id}")
                    return True
                else:
                    logger.warning(f"API更新记忆失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"API更新记忆异常: {e}")
            return False

    def _update_local_cache(
        self, 
        memory_id: str, 
        updated_content: Dict[str, Any]
    ) -> bool:
        """更新本地缓存中的记忆"""
        for user_id, memories in self.local_cache.items():
            for memory in memories:
                if memory.id == memory_id:
                    memory.content.update(updated_content)
                    memory.timestamp = datetime.now()
                    logger.info(f"成功更新本地缓存记忆: {memory_id}")
                    return True
        
        return False

    async def delete_memory(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否成功删除
        """
        try:
            # 尝试通过API删除
            if self.session:
                success = await self._delete_memory_via_api(memory_id)
                if success:
                    self._delete_from_local_cache(memory_id)
                    return True
            
            # API失败时仅删除本地缓存
            return self._delete_from_local_cache(memory_id)
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False

    async def _delete_memory_via_api(self, memory_id: str) -> bool:
        """通过API删除记忆"""
        try:
            async with self.session.delete(
                f"{self.base_url}/memories/{memory_id}"
            ) as response:
                if response.status == 204:
                    logger.info(f"成功通过API删除记忆: {memory_id}")
                    return True
                else:
                    logger.warning(f"API删除记忆失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"API删除记忆异常: {e}")
            return False

    def _delete_from_local_cache(self, memory_id: str) -> bool:
        """从本地缓存删除记忆"""
        for user_id, memories in self.local_cache.items():
            for i, memory in enumerate(memories):
                if memory.id == memory_id:
                    del memories[i]
                    logger.info(f"成功从本地缓存删除记忆: {memory_id}")
                    return True
        
        return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_memories = sum(len(memories) for memories in self.local_cache.values())
        
        return {
            "total_users": len(self.local_cache),
            "total_memories": total_memories,
            "cache_status": "connected" if self.session else "local_only",
            "last_updated": datetime.now().isoformat()
        } 