import psycopg2
from psycopg2.extras import RealDictCursor

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