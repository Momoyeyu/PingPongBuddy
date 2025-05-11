import os
import unittest
from dotenv import load_dotenv

from pingpongbuddy.agents import PingPongAgent

class TestPingPongAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 加载环境变量
        load_dotenv()
        
        # 初始化智能体
        cls.agent = PingPongAgent()
    
    def test_agent_invoke(self):
        """测试智能体调用"""
        response = self.agent.invoke(
            time="2025-05-10 14:00",
            place="北京邮电大学体育馆"
        )
        
        # 验证返回结果非空
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
        
if __name__ == "__main__":
    unittest.main() 