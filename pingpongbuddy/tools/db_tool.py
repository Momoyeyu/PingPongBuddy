import json
import os
from dotenv import load_dotenv
from langchain.tools import tool
from datetime import datetime

# 导入统一的日志模块
from pingpongbuddy.logs.logger import get_logger
from pingpongbuddy.db_utils import PingPongDatabase

# 初始化日志
logger = get_logger('pingpongbuddy.tool')

@tool
def pingpong_db_tool(action: str, params: dict) -> str:
    """Tool to interact with the PingPongBuddy database.
    Actions: store_request, find_matches, add_user.
    Params: Dictionary containing required parameters for the action.
        - store_request's params: {"user_id": int, "time": str, "place": str}
        - find_matches's params: {"time": str, "place": str}
        - add_user's params: {"username": str, "contact": str (optional)}
    Returns: JSON string with the result or error message.
    """
    logger.info(f"Tool called with action: {action}, params: {params}")
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
                error_msg = "Missing required parameters: user_id, time, place"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            request_id = db.store_request(params["user_id"], params["time"], params["place"])
            result = {"status": "success", "request_id": request_id}
            logger.info(f"Request stored successfully: {result}")
            return json.dumps(result)

        elif action == "find_matches":
            required = ["time", "place"]
            if not all(key in params for key in required):
                error_msg = "Missing required parameters: time, place"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            matches = db.find_matches(params["time"], params["place"])
            result = {"status": "success", "matches": matches}
            logger.info(f"Found {len(matches)} matches")
            return json.dumps(result)

        elif action == "add_user":
            required = ["username"]
            if not all(key in params for key in required):
                error_msg = "Missing required parameter: username"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            user_id = db.add_user(params["username"], params.get("contact"))
            result = {"status": "success", "user_id": user_id}
            logger.info(f"User added successfully: {result}")
            return json.dumps(result)

        else:
            error_msg = f"Unknown action: {action}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in tool execution: {error_msg}")
        return json.dumps({"error": error_msg})
    finally:
        db.close()