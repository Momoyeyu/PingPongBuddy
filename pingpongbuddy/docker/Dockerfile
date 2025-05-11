FROM python:3.9

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8501

# 启动应用
ENTRYPOINT ["streamlit", "run", "pingpongbuddy/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 