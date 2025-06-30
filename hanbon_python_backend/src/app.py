#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: app.py
@description: 食慧美食AI Agent主应用
@author: AI Assistant
@created: 2024
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 导入自定义模块
from agents.food_agent import FoodAgent
from memory.openmemory_client import OpenMemoryClient
from mcp_tools import MCPToolManager
from model_manager import ModelManager, ModelConfig
from config import get_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI应用将通过lifespan在下面创建

# 全局变量
config = get_config()
food_agent = None
memory_client = None
mcp_manager = None
model_manager = None
active_connections: List[WebSocket] = []

# Pydantic模型
class ChatMessage(BaseModel):
    """聊天消息模型"""
    message: str
    user_id: Optional[str] = "default"
    session_id: Optional[str] = "default"
    tools_enabled: Optional[List[str]] = []
    model: Optional[str] = None  # 新增模型选择参数
    
class ToolRequest(BaseModel):
    """工具请求模型"""
    tool_name: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = "default"

class FoodSearchRequest(BaseModel):
    """食物搜索请求模型"""
    food_name: str
    location: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    tools_used: List[str] = []
    memory_updated: bool = False
    session_id: str
    timestamp: datetime

class ModelConfigRequest(BaseModel):
    """模型配置请求模型"""
    name: str
    model: str
    api_key: str
    api_base: str
    max_tokens: int = 4000
    temperature: float = 0.7
    supports_streaming: bool = True
    description: str = ""
    enabled: bool = True

class ModelUpdateRequest(BaseModel):
    """模型更新请求模型"""
    name: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    supports_streaming: Optional[bool] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

async def startup_tasks():
    """应用启动时初始化组件"""
    global food_agent, memory_client, mcp_manager, model_manager
    
    try:
        logger.info("正在初始化瀚邦智能美食助手...")
        
        # 初始化模型管理器
        model_manager = ModelManager(config)
        
        # 初始化记忆客户端
        memory_client = OpenMemoryClient(config.OPENMEMORY_API_KEY)
        await memory_client.initialize()
        
        # 初始化MCP工具管理器（传入模型管理器）
        mcp_manager = MCPToolManager(model_manager=model_manager)
        await mcp_manager.initialize()
        
        # 初始化食物AI代理
        food_agent = FoodAgent(
            config=config,
            memory_client=memory_client,
            mcp_manager=mcp_manager,
            model_manager=model_manager
        )
        
        logger.info("瀚邦智能美食助手初始化完成！")
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        raise

async def shutdown_tasks():
    """应用关闭时清理资源"""
    logger.info("正在关闭瀚邦智能美食助手...")
    if mcp_manager:
        await mcp_manager.cleanup()
    if memory_client:
        await memory_client.close()

# 使用lifespan事件处理器替代已废弃的on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await startup_tasks()
    yield
    # 关闭时执行
    await shutdown_tasks()

# 重新创建app实例以使用lifespan
app = FastAPI(
    title="瀚邦智能美食助手API",
    description="基于AI的智能美食推荐、菜谱生成和餐厅搜索服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "食慧美食AI Agent API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "components": {
            "food_agent": food_agent is not None,
            "memory_client": memory_client is not None,
            "mcp_manager": mcp_manager is not None
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models/available")
async def get_available_models():
    """获取可用的AI模型列表"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        models = model_manager.get_all_models()
        return {
            "models": models,
            "default_model": config.DEFAULT_MODEL,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"获取可用模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@app.get("/models/{model_id}")
async def get_model_config(model_id: str):
    """获取指定模型的配置信息"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    model_config = model_manager.get_model_config(model_id)
    if not model_config:
        raise HTTPException(status_code=404, detail=f"模型 '{model_id}' 不存在")
    
    # 隐藏敏感信息
    safe_config = model_config.copy()
    if 'api_key' in safe_config:
        safe_config['api_key'] = '*' * len(safe_config['api_key'])
    
    return {
        "model_id": model_id,
        "config": safe_config
    }

@app.post("/models/{model_id}")
async def add_custom_model(model_id: str, request: ModelConfigRequest):
    """添加自定义模型"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        model_config = ModelConfig(**request.dict())
        result = await model_manager.add_custom_model(model_id, model_config)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "model_id": model_id
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"添加自定义模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")

@app.put("/models/{model_id}")
async def update_model(model_id: str, request: ModelUpdateRequest):
    """更新模型配置"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        # 只包含非None的更新字段
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")
        
        result = await model_manager.update_model(model_id, updates)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"更新模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """删除自定义模型"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        result = model_manager.delete_model(model_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"删除模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@app.post("/models/{model_id}/validate")
async def validate_model(model_id: str):
    """验证模型配置是否有效"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        model_config = model_manager.get_model_config(model_id)
        if not model_config:
            raise HTTPException(status_code=404, detail=f"模型 '{model_id}' 不存在")
        
        model_obj = ModelConfig(**model_config)
        result = await model_manager.validate_model_config(model_obj)
        
        return {
            "model_id": model_id,
            "valid": result["valid"],
            "message": result["message"],
            "test_response": result.get("test_response", "")
        }
        
    except Exception as e:
        logger.error(f"验证模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

@app.post("/models/refresh")
async def refresh_models():
    """刷新模型配置"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        model_manager.refresh_models()
        return {
            "success": True,
            "message": "模型配置刷新成功"
        }
    except Exception as e:
        logger.error(f"刷新模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")

@app.get("/tools/available")
async def get_available_tools():
    """获取可用的MCP工具列表"""
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP管理器未初始化")
    
    tools = await mcp_manager.get_available_tools()
    return {
        "tools": tools,
        "count": len(tools)
    }

@app.post("/chat")
async def chat_message(message: ChatMessage):
    """处理聊天消息"""
    if not food_agent:
        raise HTTPException(status_code=503, detail="AI Agent未初始化")
    
    # 使用指定的模型或默认模型
    selected_model = message.model or config.DEFAULT_MODEL
    
    try:
        response = await food_agent.process_message(
            message.message,
            user_id=message.user_id,
            session_id=message.session_id,
            enabled_tools=message.tools_enabled,
            model=selected_model
        )
        
        return ChatResponse(
            response=response["response"],
            tools_used=response.get("tools_used", []),
            memory_updated=response.get("memory_updated", False),
            session_id=response.get("session_id", message.session_id),
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"处理聊天消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理消息失败: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(message: ChatMessage):
    """流式聊天接口"""
    if not food_agent:
        raise HTTPException(status_code=503, detail="AI Agent未初始化")
    
    # 使用指定的模型或默认模型
    selected_model = message.model or config.DEFAULT_MODEL
    
    async def generate_response():
        try:
            async for chunk in food_agent.stream_message(
                message.message,
                user_id=message.user_id,
                session_id=message.session_id,
                enabled_tools=message.tools_enabled,
                model=selected_model
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_chunk = {
                "type": "error",
                "content": f"处理失败: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    """执行MCP工具"""
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP管理器未初始化")
    
    try:
        result = await mcp_manager.execute_tool(
            request.tool_name,
            request.parameters
        )
        return {
            "success": True,
            "result": result,
            "tool_name": request.tool_name
        }
    except Exception as e:
        logger.error(f"执行工具失败: {e}")
        raise HTTPException(status_code=500, detail=f"工具执行失败: {str(e)}")

@app.post("/api/get_ip_location")
async def get_ip_location(request: Request):
    """IP定位接口"""
    try:
        # 获取客户端IP地址
        client_ip = request.client.host
        
        # 尝试从请求头获取真实IP（处理代理情况）
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        x_real_ip = request.headers.get("X-Real-IP")
        
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        elif x_real_ip:
            client_ip = x_real_ip
            
        logger.info(f"开始IP定位，客户端IP: {client_ip}")
        
        # 获取高德地图工具
        amap_tool = mcp_manager.tools.get('amap_search')
        if not amap_tool:
            logger.error("高德地图工具未找到")
            raise HTTPException(
                status_code=503,
                detail="高德地图工具未初始化"
            )
        
        # 调用IP定位
        result = await amap_tool.get_location_by_ip(client_ip)
        
        logger.info(f"IP定位结果: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"IP定位接口错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"IP定位失败: {str(e)}"
        )

@app.post("/food/search")
async def search_food(request: FoodSearchRequest):
    """搜索美食信息"""
    if not food_agent:
        raise HTTPException(status_code=503, detail="AI Agent未初始化")
    
    try:
        result = await food_agent.search_food(
            request.food_name,
            location=request.location,
            preferences=request.preferences
        )
        return result
    except Exception as e:
        logger.error(f"搜索美食失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.get("/memory/user/{user_id}")
async def get_user_memory(user_id: str):
    """获取用户记忆"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="记忆客户端未初始化")
    
    try:
        memories = await memory_client.get_user_memories(user_id)
        return {
            "user_id": user_id,
            "memories": memories,
            "count": len(memories)
        }
    except Exception as e:
        logger.error(f"获取用户记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆失败: {str(e)}")

@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """删除指定记忆"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="记忆客户端未初始化")
    
    try:
        success = await memory_client.delete_memory(memory_id)
        if success:
            return {"success": True, "message": "记忆删除成功"}
        else:
            raise HTTPException(status_code=404, detail="记忆不存在或删除失败")
    except Exception as e:
        logger.error(f"删除记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@app.post("/memory/search")
async def search_memories(request: dict):
    """搜索用户记忆"""
    if not memory_client:
        raise HTTPException(status_code=503, detail="记忆客户端未初始化")
    
    try:
        user_id = request.get("user_id", "default")
        query = request.get("query", "")
        limit = request.get("limit", 10)
        
        results = await memory_client.search_memories(user_id, query, limit)
        return {
            "user_id": user_id,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"搜索记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket连接处理"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理消息
            if food_agent:
                selected_model = message_data.get("model") or config.DEFAULT_MODEL
                async for chunk in food_agent.stream_message(
                    message_data.get("message", ""),
                    user_id=user_id,
                    session_id=message_data.get("session_id", "default"),
                    enabled_tools=message_data.get("tools_enabled", []),
                    model=selected_model
                ):
                    await websocket.send_text(json.dumps(chunk, ensure_ascii=False))
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"用户 {user_id} 断开WebSocket连接")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 