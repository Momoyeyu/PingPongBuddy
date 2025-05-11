import os
import unittest
import json
from dotenv import load_dotenv

from pingpongbuddy.db_utils import PingPongDatabase
from pingpongbuddy.tools import pingpong_db_tool

class TestPingPongDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 加载环境变量
        load_dotenv()
        
        # 初始化测试数据库
        cls.test_db_name = "pingpongbuddy_test"
        cls.db = PingPongDatabase(
            dbname=cls.test_db_name,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cls.db.connect()
    
    @classmethod
    def tearDownClass(cls):
        # 关闭数据库连接
        cls.db.close()
        
        # 连接到默认数据库并删除测试数据库
        conn = None
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname="postgres",
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432")
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # 终止所有连接
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{cls.test_db_name}'
                AND pid <> pg_backend_pid();
            """)
            
            # 删除测试数据库
            cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db_name}")
        except Exception as e:
            print(f"Error cleaning up test database: {e}")
        finally:
            if conn:
                conn.close()
    
    def test_add_user(self):
        """测试添加用户"""
        user_id = self.db.add_user("测试用户", "test@example.com")
        self.assertIsNotNone(user_id)
    
    def test_store_request(self):
        """测试存储约球请求"""
        # 先添加用户
        user_id = self.db.add_user("测试用户2", "test2@example.com")
        
        # 存储约球请求
        request_id = self.db.store_request(user_id, "2025-05-15", "测试体育馆")
        self.assertIsNotNone(request_id)
    
    def test_find_matches(self):
        """测试寻找匹配"""
        # 先添加用户并存储请求
        user_id = self.db.add_user("测试用户3", "test3@example.com")
        self.db.store_request(user_id, "2025-05-20", "匹配测试体育馆")
        
        # 寻找匹配
        matches = self.db.find_matches("2025-05-20", "匹配测试体育馆")
        self.assertIsInstance(matches, list)
    
    def test_db_tool(self):
        """测试数据库工具"""
        # 测试添加用户
        result = pingpong_db_tool("add_user", {"username": "工具测试用户", "contact": "tool@example.com"})
        result_data = json.loads(result)
        self.assertEqual(result_data["status"], "success")
        self.assertIn("user_id", result_data)
        
        # 使用返回的用户ID测试存储请求
        user_id = result_data["user_id"]
        result = pingpong_db_tool("store_request", {
            "user_id": user_id,
            "time": "2025-06-01",
            "place": "工具测试体育馆"
        })
        result_data = json.loads(result)
        self.assertEqual(result_data["status"], "success")
        
        # 测试查找匹配
        result = pingpong_db_tool("find_matches", {
            "time": "2025-06-01",
            "place": "工具测试体育馆"
        })
        result_data = json.loads(result)
        self.assertEqual(result_data["status"], "success")
        self.assertIn("matches", result_data)
        
if __name__ == "__main__":
    unittest.main() 