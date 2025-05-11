# 友小智 - PingPongBuddy

友小智——PingPongBuddy是一款支持乒乓球友约球的智能体，基于Langchain框架开发，使用智谱的GLM-4-Flash作为底层模型。

## 项目结构

```
├── assets               # 静态资源
├── pingpongbuddy        # 主项目代码
│   ├── agents           # 智能体代码
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

### 使用Docker
```bash
docker-compose up -d
```

## 功能特点

- 乒乓球约球智能匹配
- 基于时间和场地的智能推荐
- 支持用户注册和管理
- 简洁直观的用户界面

## 技术栈

- Langchain框架
- 智谱GLM-4-Flash大语言模型
- PostgreSQL数据库
- Streamlit前端界面
- Docker容器化部署 