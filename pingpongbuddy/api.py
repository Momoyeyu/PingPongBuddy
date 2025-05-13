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
    input_text: str = None
    time: str = None
    place: str = None
    skill_level: str = None
    opponent_count: str = None
    opponent_skill_level: str = None
    match_type: str = None
    additional_notes: str = None

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
        "description": "乒乓球约球智能助手，支持乒乓球友约球、球友匹配和相关查询",
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
                "description": "提供乒乓球约球服务，可以接受自然语言或结构化输入，支持约球、查询和一般性问题回答",
                "tags": ["乒乓球", "约球", "匹配", "查询"],
                "version": "1.0.0",
                "lastModifiedTime": datetime.now(timezone.utc).isoformat().replace('+00:00', '+08:00'),
                "inputTypes": ["application/json", "text/plain"],
                "outputTypes": ["application/json", "text/plain"],
                "examples": [
                    {
                        "input": '{"input_text": "我想明天下午两点在北邮体育馆打乒乓球"}',
                        "output": "我已收到你的约球请求，将为你匹配明天下午两点在北邮体育馆打乒乓球的球友。"
                    },
                    {
                        "input": '{"time": "2023-09-15 14:00", "place": "北京邮电大学体育馆", "skill_level": "中级"}',
                        "output": "我已收到你的约球请求，将为你匹配2023年9月15日14:00在北京邮电大学体育馆打乒乓球的球友。你的技术水平是中级，我会寻找适合的球友。"
                    },
                    {
                        "input": '{"input_text": "查询今天有哪些约球信息"}',
                        "output": "今天有3条约球信息：1. 14:00在北邮体育馆有2人约球，2. 16:30在清华大学体育馆有1人约球，3. 19:00在北邮体育馆有4人约球。"
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
        # 直接转发所有参数（包括可选参数）到智能体
        response = agent.invoke(
            input_text=request.input_text,
            time=request.time,
            place=request.place,
            skill_level=request.skill_level,
            opponent_count=request.opponent_count,
            opponent_skill_level=request.opponent_skill_level,
            match_type=request.match_type,
            additional_notes=request.additional_notes
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