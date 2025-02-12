from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import io
import httpx
import requests
import json
import os
import sys
from pathlib import Path

# 导入天气推荐相关函数
from .app import weather_recommendations

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the new AsyncOpenAI client
from openai import OpenAI
import asyncio
import uvicorn

# 根据环境变量加载配置
env = os.getenv('ENV', 'development')
if env == 'development':
    from config.development import *
else:
    from config.production import *

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建一个路由前缀
api_router = APIRouter(prefix="/api")


# Initialize the OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

# 添加聚合数据 API 配置
JUHE_API_KEY = "49ed17916d463840e8d7f45183771198"
JUHE_RECIPE_URL = "http://apis.juhe.cn/fapigx/caipu/query"

# 添加百度图片搜索API配置
BAIDU_IMG_API_ID = "10002477"  # 这里需要替换为你的实际ID
BAIDU_IMG_API_KEY = "3752609fbeba1c8318a147a8f412bdf3"  # 这里需要替换为你的实际KEY
BAIDU_IMG_API_URL = "https://cn.apihz.cn/api/img/apihzimgbaidu.php"

@api_router.get("/generate_food_image")
async def generate_food_image(food: str):
    if not food:
        return "请提供食物名称", 400

    async def generate():
        try:
            # 构建API请求参数
            params = {
                "id": BAIDU_IMG_API_ID,
                "key": BAIDU_IMG_API_KEY,
                "words": food,
                "limit": 1,  # 只获取一张图片
                "page": 1,
                "type": 1  # 返回百度预览图地址
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(BAIDU_IMG_API_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["code"] == 200 and data["res"]:
                        # 获取第一张图片的URL
                        image_url = data["res"][0]
                        
                        # 下载图片
                        img_response = await client.get(image_url)
                        if img_response.status_code == 200:
                            # 将图片转换为base64
                            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            yield f"data: {image_base64}"
                        else:
                            yield f"data: Error: Failed to download image"
                    else:
                        yield f"data: Error: No images found"
                else:
                    yield f"data: Error: Failed to fetch from API: {response.status_code}"
                
        except Exception as e:
            yield f"data: Error: {str(e)}"

    return StreamingResponse(generate(), media_type='text/event-stream')

@api_router.get("/generate_food_image_baidu")
async def generate_food_image_baidu(food: str, page: int = 1, limit: int = 1):
    """
    使用百度图片搜索API获取食物图片URL
    
    Args:
        food (str): 要搜索的食物名称
        page (int): 页码，默认1
        limit (int): 返回结果数量，默认1，最大100
    """
    if not food:
        return JSONResponse(content={"code": 400, "msg": "请提供食物名称"}, status_code=400)

    # 限制limit的范围
    if limit > 100:
        limit = 100

    try:
        # 使用默认域名接口，更稳定可靠
        api_url = "https://cn.apihz.cn/api/img/apihzimgbaidu.php"

        # 构建API请求参数
        params = {
            "id": BAIDU_IMG_API_ID,
            "key": BAIDU_IMG_API_KEY,
            "words": food,
            "limit": limit,
            "page": page,
            "type": 1  # 返回百度预览图地址
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data["code"] == 200 and data["res"]:
                    return JSONResponse(content={
                        "code": 200,
                        "msg": "success",
                        "data": data["res"]
                    })
                else:
                    return JSONResponse(content={
                        "code": 400,
                        "msg": data.get("msg", "未找到相关图片"),
                        "data": []
                    })
            else:
                return JSONResponse(content={
                    "code": response.status_code,
                    "msg": "API请求失败",
                    "data": []
                })
            
    except Exception as e:
        return JSONResponse(content={
            "code": 500,
            "msg": str(e),
            "data": []
        })

@api_router.get("/call_openai")
async def call_openai(query: str):
    prompt = f"你是一个营养师，请计算'{query}'的热量。要求：1. 只输出大概的卡路里数值；2. 默认按照100克重量计算；3. 数值后面加上'卡路里'三个字。"

    try:
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "你是一个营养师，请简洁地回答食物的热量，只需要提供卡路里数值。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.5,
            stream=False
        )
        
        return JSONResponse(content={"content": response.choices[0].message.content.strip()})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@api_router.get("/get_recipe")
async def get_recipe(food: str):
    if not food:
        return "请提供食物名称", 400

    async def generate():
        try:
            # 1. 首先获取菜谱基本信息
            basic_info = await get_basic_nutrition(food)
            if basic_info:
                yield f"data: **营养价值**\n{basic_info}\n\n"
            
            # 2. 然后获取聚合数据的菜谱信息
            import aiohttp
            async with aiohttp.ClientSession() as session:
                params = {
                    "key": JUHE_API_KEY,
                    "word": food,
                    "num": 1,
                }
                
                async with session.get(JUHE_RECIPE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["error_code"] == 0 and data["result"]["list"]:
                            recipe = data["result"]["list"][0]
                            
                            # 输出食材信息
                            if recipe["yuanliao"]:
                                yield f"data: **主料**\n{recipe['yuanliao']}\n\n"
                            
                            if recipe["tiaoliao"]:
                                yield f"data: **调料**\n{recipe['tiaoliao']}\n\n"
                            
                            # 输出烹饪步骤
                            yield f"data: **烹饪步骤**\n\n"
                            steps = recipe["zuofa"].split("；")
                            for i, step in enumerate(steps, 1):
                                if step.strip():
                                    yield f"data: {i}. {step.strip()}。\n\n"
                                    await asyncio.sleep(0.3)
                            
                            # 输出特色和小贴士
                            if recipe["texing"]:
                                yield f"data: **特色**\n{recipe['texing']}\n\n"
                            
                            if recipe["tishi"]:
                                yield f"data: **烹饪小贴士**\n{recipe['tishi']}\n\n"
                            
                        else:
                            yield f"data: 抱歉，没有找到{food}的相关菜谱信息。\n\n"
                    else:
                        yield f"data: 获取菜谱信息失败，请稍后重试。\n\n"
                        
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')

@api_router.get("/get_qwen_recipe")
async def get_qwen_recipe(food: str):
    if not food:
        return "请提供食物名称", 400

    prompt = f"""请为我详细介绍如何制作{food}。要求：
1. 分别列出主料、调料；
2. 详细的步骤说明；
3. 烹饪小贴士。
请按以下格式输出，确保每个部分都有标题：

**营养价值**
(营养价值说明)

**主料**
- 材料1：用量
- 材料2：用量
(依此类推)

**调料**
- 调料1：用量
- 调料2：用量
(依此类推)

**烹饪步骤**
1. 第一步
2. 第二步
(依此类推)

**烹饪小贴士**
(实用建议)"""

    async def generate():
        try:
            response = client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {"role": "system", "content": "你是一个专业的中餐厨师，精通各种美食的制作方法。请用markdown格式输出内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                if content:
                    yield f"data: {content}\n\n"
                    
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')

@api_router.get("/get_weather_recommendations")
async def get_weather_recommendations():
    """
    获取基于天气的食物推荐
    """
    return await weather_recommendations()

async def get_basic_nutrition(food: str):
    """获取食材的基本营养信息"""
    try:
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "你是一个专业的营养师，请简要介绍食材的营养价值。"},
                {"role": "user", "content": f"请简要介绍{food}的主要营养价值，用一句话概括。"}
            ],
            max_tokens=50,
            temperature=0.7,
            stream=False
        )
        return response.choices[0].message.content
    except Exception:
        return None

# 将 api_router 挂载到主应用
app.include_router(api_router)

def main():
    uvicorn.run(app, host=API_HOST, port=API_PORT)

if __name__ == "__main__":
    main()

# 运行应用程序
# 使用命令 `uvicorn src.sse:app --reload --port=7999` 来启动 FastAPI 应用
