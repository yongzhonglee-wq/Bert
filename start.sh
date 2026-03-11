#!/bin/bash
# 简单启动脚本 - 使用 APScheduler 直接调度，不需要 Redis 和 Celery

if [ -f .env ]; then
    export $(cat .env | xargs)
fi

echo "启动新闻推送服务..."
python3 simple_server.py
