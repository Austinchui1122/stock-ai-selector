FROM python:3.9-slim

WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY src/ src/
COPY config/ config/
COPY .env .

# 安装依赖
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8501

# 设置环境变量
ENV PYTHONPATH=/app

# 启动应用
CMD ["streamlit", "run", "src/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 