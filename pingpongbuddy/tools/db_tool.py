import json
import os
from dotenv import load_dotenv
from langchain.tools import tool

from pingpongbuddy.db_utils import PingPongDatabase

@tool
def pingpong_db_tool(action: str, params: dict) -> str:
    """
    Tool to interact with the PingPongBuddy database.
    Actions: store_request, find_matches, add_user.
    Params: Dictionary containing required parameters for the action.
        - store_request's params: {"user_id": int, "time": str, "place": str}
        - find_matches's params: {"time": str, "place": str}
        - add_user's params: {"username": str, "contact": str (optional)}
    Returns: JSON string with the result or error message.
    """
    try:
        # 初始化数据库（从环境变量获取配置）
        load_dotenv()
        db = PingPongDatabase(
            dbname=os.getenv("DB_NAME", "pingpongbuddy"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        db.connect()

        if action == "store_request":
            required = ["user_id", "time", "place"]
            if not all(key in params for key in required):
                return json.dumps({"error": "Missing required parameters: user_id, time, place"})
            request_id = db.store_request(params["user_id"], params["time"], params["place"])
            return json.dumps({"status": "success", "request_id": request_id})

        elif action == "find_matches":
            required = ["time", "place"]
            if not all(key in params for key in required):
                return json.dumps({"error": "Missing required parameters: time, place"})
            matches = db.find_matches(params["time"], params["place"])
            return json.dumps({"status": "success", "matches": matches})

        elif action == "add_user":
            required = ["username"]
            if not all(key in params for key in required):
                return json.dumps({"error": "Missing required parameter: username"})
            user_id = db.add_user(params["username"], params.get("contact"))
            return json.dumps({"status": "success", "user_id": user_id})

        else:
            return json.dumps({"error": f"Unknown action: {action}"})

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close() 