# 友小智 - PingPongBuddy SDK

本 SDK 提供了访问友小智 - PingPongBuddy API 服务的 Python 客户端。

## 安装

直接从项目目录安装：

```bash
cd PingPongBuddy
pip install -e .
```

## 使用示例

```python
from pingpongbuddy.sdk import PingPongBuddyClient

# 创建客户端
client = PingPongBuddyClient(base_url="http://localhost:8000")

# 获取智能体能力描述（ACS）
agent_spec = client.get_agent_spec()
print("智能体名称:", agent_spec["name"])
print("智能体描述:", agent_spec["description"])

# 发起约球请求
result = client.match(
    time="2023-09-15 14:00",
    place="北京邮电大学体育馆"
)
print("约球结果:", result["message"])

# 检查 API 服务健康状态
health = client.health_check()
print("健康状态:", health["status"])
```

## API 文档

### PingPongBuddyClient

#### 初始化

```python
client = PingPongBuddyClient(base_url="http://localhost:8000", api_key=None)
```

- `base_url` - API 服务的基础 URL
- `api_key` - API 密钥（如果启用了认证）

#### 方法

##### get_agent_spec()

获取智能体能力描述（ACS）。

返回：符合 ACS 协议的智能体能力描述（字典）

##### match(time, place)

发起乒乓球约球请求。

参数：
- `time` - 约球时间，如 "2023-09-15 14:00"
- `place` - 约球地点，如 "北京邮电大学体育馆"

返回：API 响应结果（字典）

##### health_check()

检查 API 服务健康状态。

返回：健康状态信息（字典） 