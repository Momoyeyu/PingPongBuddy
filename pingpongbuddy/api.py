from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pingpongbuddy.agents import PingPongAgent

# 创建FastAPI应用
app = FastAPI(
    title="友小智 - PingPongBuddy API",
    description="乒乓球约球智能体 API 服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建智能体实例
agent = PingPongAgent()

# 请求模型
class MatchRequest(BaseModel):
    time: str
    place: str

# ACS 模型
class ProviderInfo(BaseModel):
    name: str
    url: str
    license: str

class SkillExample(BaseModel):
    input: str
    output: str

class SDK(BaseModel):
    language: str
    url: str

class Skill(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    version: str
    lastModifiedTime: str
    inputTypes: list[str]
    outputTypes: list[str]
    examples: list[SkillExample]
    SDKs: list[SDK]

class ACS(BaseModel):
    AIC: str
    name: str
    description: str
    url: str
    version: str
    registrationTime: str
    lastModifiedTime: str
    status: str
    provider: ProviderInfo
    authentication: list[str]
    skills: list[Skill]


@app.get("/")
async def root():
    return {"message": "友小智 - PingPongBuddy API 服务"}

# ACS 能力描述接口
@app.get("/agent_spec.json")
async def get_agent_spec():
    # 创建符合 ACS 协议的智能体能力描述
    acs = {
        "AIC": "01001560001000625000000000000147",  # 示例 AIC
        "name": "PingPongBuddy",
        "description": "乒乓球约球智能助手，支持乒乓球友约球和球友匹配",
        "url": "https://pingpongbuddy.example.com",
        "version": "1.0.0",
        "registrationTime": "2023-08-15T08:30:00+08:00",
        "lastModifiedTime": datetime.now(timezone.utc).isoformat().replace('+00:00', '+08:00'),
        "status": "active",
        "provider": {
            "name": "PingPongBuddy Team",
            "url": "https://pingpongbuddy.example.com",
            "license": "示例备案号"
        },
        "authentication": ["API Key"],
        "skills": [
            {
                "id": "match:01",
                "name": "乒乓球约球",
                "description": "根据用户提供的时间和地点，进行乒乓球约球匹配",
                "tags": ["乒乓球", "约球", "匹配"],
                "version": "1.0.0",
                "lastModifiedTime": datetime.now(timezone.utc).isoformat().replace('+00:00', '+08:00'),
                "inputTypes": ["application/json"],
                "outputTypes": ["application/json", "text/plain"],
                "examples": [
                    {
                        "input": '{"time": "2023-09-15 14:00", "place": "北京邮电大学体育馆"}',
                        "output": "我已收到你的约球请求，将为你匹配2023年9月15日14:00在北京邮电大学体育馆打乒乓球的球友"
                    }
                ],
                "SDKs": [
                    {
                        "language": "Python",
                        "url": "https://pingpongbuddy.example.com/sdk/python.zip"
                    }
                ]
            }
        ]
    }
    
    return acs

# 约球匹配接口
@app.post("/api/v1/match")
async def match(request: MatchRequest):
    try:
        response = agent.invoke(
            time=request.time,
            place=request.place
        )
        
        return {
            "status": "success",
            "message": response,
            "request_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查接口
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# 本地运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pingpongbuddy.api:app", host="0.0.0.0", port=8555, reload=True) 