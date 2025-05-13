import requests

class PingPongBuddyClient:
    """友小智 - PingPongBuddy API 客户端
    
    用于访问 PingPongBuddy API 服务的 Python 客户端 SDK。
    """
    
    def __init__(self, base_url="http://localhost:8555", api_key=None):
        """初始化 PingPongBuddy 客户端
        
        Args:
            base_url: API 服务的基础 URL
            api_key: API 密钥（如果有的话）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_agent_spec(self):
        """获取智能体能力描述（ACS）
        
        Returns:
            dict: 符合 ACS 协议的智能体能力描述
        """
        response = requests.get(f"{self.base_url}/agent_spec.json", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def match(self, input_text=None, time=None, place=None, **optional_params):
        """发起乒乓球约球请求或其他对话
        
        Args:
            input_text: 直接对话输入文本，如 "我想约球" 或 "查询明天的约球"
            time: 约球时间，如 "2023-09-15 14:00"（可选）
            place: 约球地点，如 "北京邮电大学体育馆"（可选）
            **optional_params: 其他可选参数
                - skill_level: 技术水平，如 "初级"
                - opponent_count: 球友数量，如 "2"
                - opponent_skill_level: 球友技术水平，如 "中级"
                - match_type: 比赛类型，如 "友谊赛"
                - additional_notes: 额外备注
            
        Returns:
            dict: API 响应结果
            
        Examples:
            # 使用直接对话方式
            client.match(input_text="我想明天上午在北邮打球")
            
            # 使用结构化输入方式
            client.match(time="2023-09-15 14:00", place="北京邮电大学体育馆")
            
            # 使用结构化输入+高级选项
            client.match(
                time="2023-09-15 14:00",
                place="北京邮电大学体育馆",
                skill_level="中级",
                opponent_count="2"
            )
        """
        # 构建请求数据
        data = {
            "input_text": input_text,
            "time": time,
            "place": place
        }
        
        # 添加其他可选参数
        for key, value in optional_params.items():
            data[key] = value
        
        response = requests.post(
            f"{self.base_url}/api/v1/match", 
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """检查 API 服务健康状态
        
        Returns:
            dict: 健康状态信息
        """
        response = requests.get(f"{self.base_url}/health", headers=self.headers)
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = PingPongBuddyClient()
    
    # 获取智能体能力描述
    agent_spec = client.get_agent_spec()
    print("智能体名称:", agent_spec["name"])
    print("智能体描述:", agent_spec["description"])
    
    # 获取健康状态
    health = client.health_check()
    print("健康状态:", health["status"])
    
    # 示例1：使用直接对话方式
    try:
        result = client.match(input_text="我想明天下午2点在北邮体育馆打乒乓球，我是初学者")
        print("约球结果:", result["message"])
    except Exception as e:
        print("请求失败:", str(e))
        
    # 示例2：使用结构化输入方式
    try:
        result = client.match(
            time="2023-09-15 14:00",
            place="北京邮电大学体育馆",
            skill_level="中级",
            opponent_count="2"
        )
        print("约球结果:", result["message"])
    except Exception as e:
        print("请求失败:", str(e)) 