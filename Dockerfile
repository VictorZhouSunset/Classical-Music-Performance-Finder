FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y supervisor

# 从项目根目录复制到云端镜像内部的工作目录（也就是之前设置的WORKDIR）
COPY . . 

RUN chmod +x start_web.sh start_worker.sh

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 当执行apt-get install -y supervisor时，默认安装路径是/usr/bin/supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]