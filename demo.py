#%% md
# # 友小智——PingPongBuddy
# 
# 友小智——PingPongBuddy是一款支持乒乓球友约球的智能体，采用Langchain框架进行开发，模型选择了智谱的GLM-4-Flash。
#%% md
# ## 引入依赖
#%%
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain.tools import tool
import json
import os
#%% md
# 引入环境变量
#%%
from dotenv import load_dotenv
load_dotenv();
#%% md
# ## 数据库
# 
# 为了存储约球信息，需要让智能体能够使用数据库。简单起见，数据库我们选择PostgreSQL，并实现对应的工具。
#%%
class PingPongDatabase:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.conn_params = {"dbname": dbname, "user": user, "password": password, "host": host, "port": port}
        self.default_conn_params = {"dbname": "postgres", "user": user, "password": password, "host": host, "port": port}
        self.conn = None
        self.cursor = None

    def _create_database(self):
        try:
            conn = psycopg2.connect(**self.default_conn_params)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.dbname,))
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.dbname}")
            cursor.close()
            conn.close()
        except Exception as e:
            raise Exception(f"Error creating database: {e}")

    def connect(self):
        try:
            self._create_database()
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self._create_table()
        except Exception as e:
            raise Exception(f"Database connection error: {e}")

    def _create_table(self):
        create_tables_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            contact VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 创建ENUM类型（如果不存在）
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'request_status') THEN
                CREATE TYPE request_status AS ENUM ('open', 'closed', 'cancelled', 'matched');
            END IF;
        END $$;

        CREATE TABLE IF NOT EXISTS pingpong_requests (
            request_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            time DATE NOT NULL,
            place VARCHAR(100) NOT NULL,
            status request_status NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        -- 创建索引（如果不存在）
        CREATE INDEX IF NOT EXISTS idx_pingpong_requests_time_place ON pingpong_requests (time, place);
        CREATE INDEX IF NOT EXISTS idx_pingpong_requests_user_id ON pingpong_requests (user_id);
        CREATE INDEX IF NOT EXISTS idx_pingpong_requests_status ON pingpong_requests (status);

        -- 创建函数（如果不存在）
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        -- 创建触发器（如果不存在）
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgrelid = 'pingpong_requests'::regclass
                AND tgname = 'update_pingpong_requests_updated_at'
            ) THEN
                CREATE TRIGGER update_pingpong_requests_updated_at
                BEFORE UPDATE ON pingpong_requests
                FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
            END IF;
        END $$;
        """
        self.cursor.execute(create_tables_query)
        self.conn.commit()
    def store_request(self, user_id, time, place):
        insert_query = """
        INSERT INTO pingpong_requests (user_id, time, place, status)
        VALUES (%s, %s, %s, 'open')
        RETURNING request_id;
        """
        self.cursor.execute(insert_query, (user_id, time, place))
        self.conn.commit()
        return self.cursor.fetchone()['request_id']

    def find_matches(self, time, place):
        select_query = """
        SELECT
            r.request_id,
            r.user_id,
            u.username,
            u.contact,
            r.time::TEXT,
            r.place,
            r.status::TEXT,
            r.created_at::TEXT,
            r.updated_at::TEXT,
            ABS(EXTRACT(EPOCH FROM (r.time::TIMESTAMP - %s::TIMESTAMP))) AS time_distance
        FROM pingpong_requests r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.place = %s
          AND r.status = 'open'
        ORDER BY time_distance ASC;
        """
        self.cursor.execute(select_query, (time, place))
        return self.cursor.fetchall()

    def add_user(self, username, contact=None):
        insert_query = """
        INSERT INTO users (username, contact)
        VALUES (%s, %s)
        RETURNING user_id;
        """
        self.cursor.execute(insert_query, (username, contact))
        self.conn.commit()
        return self.cursor.fetchone()['user_id']

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
#%% md
# LangChain 数据库工具
#%%
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
        # 初始化数据库（假设从环境变量获取配置）
        from dotenv import load_dotenv
        import os
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
#%% md
# 初始化数据库
#%%
db = PingPongDatabase(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)
db.connect()
#%% md
# ## 智能体定义
#%%
prompt_template = ChatPromptTemplate(
    [
        ('system', "你是一个乒乓球约球助手，当用户想要约球时，你会将用户的请求存储到数据库中，并帮助用户寻找合适的球友。"),
        ('human', "我想要在{time}、{place}打乒乓球，请你帮我寻找合适的球友。")
    ]
)
#%%
model = ChatOpenAI(
    model = 'glm-4-flash',
    openai_api_base = "https://open.bigmodel.cn/api/paas/v4",
    max_tokens = 500,
    temperature = 0.7
)
#%%
def output_parser(output):
    parser_model = ChatOpenAI(
        model = 'glm-3-turbo',
        temperature = 0.3,
        openai_api_base = "https://open.bigmodel.cn/api/paas/v4"
    )
    message = "你需要将传入的文本进行改写，尽可能地更加自然简洁，专注于关键信息。这是你需要改写的文本:`{text}`"
    return parser_model.invoke(message.format(text=output))
#%%
chain = (
    prompt_template
    | model
    | output_parser
)
#%% md
# ## 测试
#%%
response = chain.invoke({"time": "2025-05-10 14:00", "place": "北京邮电大学体育馆"})
print(response.content)