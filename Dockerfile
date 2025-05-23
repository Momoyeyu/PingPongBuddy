FROM harbor.lab.bigai.site/junjie-su/pingpongbuddy:latest

# 复制项目文件
COPY scripts .

# 暴露端口
EXPOSE 8501

# 启动应用
ENTRYPOINT ["streamlit", "run", "pingpongbuddy/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
