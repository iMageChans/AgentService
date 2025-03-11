FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装依赖
COPY requirements/base.txt base.txt
COPY requirements/prod.txt prod.txt
RUN pip install --no-cache-dir -r prod.txt

# 复制项目文件
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# 暴露8002端口
EXPOSE 8002

# 运行服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]