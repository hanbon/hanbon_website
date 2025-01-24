from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

# Import the new AsyncOpenAI client
from openai import OpenAI
import asyncio
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust this in production
    allow_headers=["*"],  # Allows all headers, adjust this in production
)

# 设置 OpenAI API 密钥
api_key = 'sk-pRHCvVoHsPdLIihiA5B6D67f56F649BfB905C32aE29a9fB4'  # 替换为你的实际 OpenAI API 密钥

# Initialize the AsyncOpenAI client
client = OpenAI(
    base_url="https://openai.tongdaai.com/v1",
    api_key=api_key
)

@app.get("/stream")
async def stream(count: int = 5):
    async def generate():
        # 模拟流式输出
        for i in range(count):
            yield f"data: 生成示例结果{i + 1}...\n\n"
            await asyncio.sleep(1)  # 模拟延迟
    return StreamingResponse(generate(), media_type='text/event-stream')

@app.get("/call_openai")
async def call_openai(query: str):
    prompt = f"你是一个营养师，请计算'{query}'的热量。要求：1. 只输出大概的卡路里数值；2. 默认按照100克重量计算；3. 数值后面加上'卡路里'三个字。"

    async def generate():
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个营养师，请简洁地回答食物的热量，只需要提供卡路里数值。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.5,
                stream=True
            )
            
            for chunk in response:
                # Access the content correctly
                content = chunk.choices[0].delta.content.strip() if chunk.choices[0].delta.content else ""
                yield f"data: {content}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')

def main():
    uvicorn.run(app, host="0.0.0.0", port=7999)

if __name__ == "__main__":
    main()

# 运行应用程序
# 使用命令 `uvicorn hanbon_python_backend.src.see:app --reload` 来启动 FastAPI 应用
