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
client = PingPongBuddyClient(base_url="http://localhost:8555")

# 获取智能体能力描述（ACS）
agent_spec = client.get_agent_spec()
print("智能体名称:", agent_spec["name"])
print("智能体描述:", agent_spec["description"])

# 方式1：自然语言方式交互
result = client.match(
    input_text="我想明天下午两点在北邮体育馆打乒乓球，我是初级水平"
)
print("约球结果:", result["message"])

# 方式2：结构化数据方式交互
result = client.match(
    time="2023-09-15 14:00",
    place="北京邮电大学体育馆"
)
print("约球结果:", result["message"])

# 方式3：结构化数据 + 高级选项
result = client.match(
    time="2023-09-15 14:00",
    place="北京邮电大学体育馆",
    skill_level="中级", 
    opponent_count="2",
    opponent_skill_level="中级",
    match_type="友谊赛",
    additional_notes="希望打单打和双打都可以"
)
print("约球结果:", result["message"])

# 查询功能 - 直接使用自然语言
result = client.match(
    input_text="查询明天有哪些约球信息"
)
print("查询结果:", result["message"])

# 检查 API 服务健康状态
health = client.health_check()
print("健康状态:", health["status"])
```

## API 文档

### PingPongBuddyClient

#### 初始化

```python
client = PingPongBuddyClient(base_url="http://localhost:8555", api_key=None)
```

- `base_url` - API 服务的基础 URL
- `api_key` - API 密钥（如果启用了认证）

#### 方法

##### get_agent_spec()

获取智能体能力描述（ACS）。

返回：符合 ACS 协议的智能体能力描述（字典）

##### match(input_text=None, time=None, place=None, **optional_params)

与智能体交互，可用于约球、查询或其他对话。

参数：
- `input_text` - 直接对话输入文本，如 "我想约球" 或 "查询明天的约球"
- `time` - 约球时间，如 "2023-09-15 14:00"（可选）
- `place` - 约球地点，如 "北京邮电大学体育馆"（可选） 
- `**optional_params` - 其他可选参数:
  - `skill_level` - 技术水平，如 "初级"
  - `opponent_count` - 球友数量，如 "2"
  - `opponent_skill_level` - 球友技术水平，如 "中级"
  - `match_type` - 比赛类型，如 "友谊赛"
  - `additional_notes` - 额外备注

返回：API 响应结果（字典）

##### health_check()

检查 API 服务健康状态。

返回：健康状态信息（字典） 