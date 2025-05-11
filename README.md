# 友小智 - PingPongBuddy

友小智——PingPongBuddy是一款支持乒乓球友约球的智能体，基于Langchain框架开发，使用智谱的GLM-4-Flash作为底层模型。

## 项目结构

```
├── assets               # 静态资源
├── pingpongbuddy        # 主项目代码
│   ├── agents           # 智能体代码
│   ├── api.py           # API 服务
│   ├── data             # 数据文件
│   ├── docker           # Docker相关配置
│   │   └── aizynthfinder # 特定容器配置
│   ├── frontend         # 前端代码
│   └── tools            # 工具函数
└── tests                # 测试代码
```

## 环境配置

1. 复制环境变量示例文件并修改为你的配置
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入你的智谱API密钥和数据库配置

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

### 本地运行
```bash
streamlit run pingpongbuddy/frontend/app.py
```

或使用入口脚本：
```bash
python run.py --mode frontend
```

### API 模式运行
支持符合 ACS（Agent Capability Specification）协议的 API 模式：

```bash
python run.py --mode api --host 0.0.0.0 --port 8000
```

API 服务将在 http://localhost:8000 上启动，支持以下端点：

- `GET /agent_spec.json` - 获取符合 ACS 协议的智能体能力描述
- `POST /api/v1/match` - 乒乓球约球匹配服务
- `GET /health` - 健康检查

使用示例（Python）：

```python
import requests

# 查询智能体能力描述
response = requests.get("http://localhost:8000/agent_spec.json")
print(response.json())

# 使用约球匹配服务
data = {
    "time": "2023-09-15 14:00",
    "place": "北京邮电大学体育馆"
}
response = requests.post("http://localhost:8000/api/v1/match", json=data)
print(response.json())
```

### 使用Docker
```bash
docker-compose up -d
```

## 功能特点

- 乒乓球约球智能匹配
- 基于时间和场地的智能推荐
- 支持用户注册和管理
- 简洁直观的用户界面
- 符合 ACS 协议的 API 接口

## 技术栈

- Langchain框架
- 智谱GLM-4-Flash大语言模型
- PostgreSQL数据库
- Streamlit前端界面
- FastAPI API服务
- Docker容器化部署

## ACS 协议支持

友小智——PingPongBuddy支持智能体互联网的 ACPs 智能体协作协议族中的智能体能力描述（Agent Capability Specification，ACS）标准。

查看智能体能力描述：
```bash
curl http://localhost:8000/agent_spec.json
``` 