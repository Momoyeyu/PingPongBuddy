FROM harbor.lab.bigai.site/momoyeyu/pingpongbuddy:latest

WORKDIR /app

# 复制项目文件
COPY . .

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 8501
EXPOSE 8555
