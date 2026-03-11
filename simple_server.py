#!/usr/bin/env python3
"""
简单的HTTP服务器，提供新闻推送触发接口
"""

from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from news_fetcher import NewsFetcher
from wechat_notifier import WeChatNotifier
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def fetch_and_send_news():
    """获取并发送新闻"""
    from datetime import datetime
    from pytz import timezone

    shanghai_tz = timezone('Asia/Shanghai')
    current_time = datetime.now(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"========== 定时任务触发时间: {current_time} (北京时间) ==========")

    try:
        fetcher = NewsFetcher(Config.NEWS_SOURCES)
        all_news = fetcher.fetch_all_news()

        notifier = WeChatNotifier()
        success = notifier.send_news_notification(all_news)

        if success:
            logger.info("定时新闻推送成功！")
        else:
            logger.error("定时新闻推送失败")

    except Exception as e:
        logger.error(f"定时新闻推送异常: {e}")


# 启动定时任务
from pytz import timezone
from datetime import datetime

shanghai_tz = timezone('Asia/Shanghai')
current_time = datetime.now(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S')
logger.info(f"当前北京时间: {current_time}")

scheduler = BackgroundScheduler(timezone=shanghai_tz)

# 解析cron表达式
cron_expr = Config.CRON_SCHEDULE
parts = cron_expr.split()
if len(parts) == 5:
    minute, hour, day, month, day_of_week = parts
    scheduler.add_job(
        func=fetch_and_send_news,
        trigger=CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone=shanghai_tz
        ),
        id='news_push_task',
        name='每日新闻推送'
    )
    scheduler.start()
    logger.info(f"定时任务已启动，执行时间: {cron_expr} (北京时间)")
    logger.info(f"下次执行时间: {scheduler.get_job('news_push_task').next_run_time}")


@app.route('/')
def index():
    return '''
    <h1>新闻聚合应用</h1>
    <p>API接口:</p>
    <ul>
        <li><a href="/health">健康检查</a></li>
        <li><a href="/trigger" onclick="return confirm('确定要手动触发新闻推送吗？');">手动触发推送</a></li>
        <li><a href="/preview">预览新闻内容</a></li>
    </ul>
    '''

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "message": "News Aggregator is running"
    })

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_news():
    """手动触发新闻推送"""
    logger.info("手动触发新闻推送任务...")

    try:
        # 获取新闻
        fetcher = NewsFetcher(Config.NEWS_SOURCES)
        all_news = fetcher.fetch_all_news()

        # 发送推送
        notifier = WeChatNotifier()
        success = notifier.send_news_notification(all_news)

        if success:
            logger.info("新闻推送成功！")
            return jsonify({
                "status": "success",
                "message": "新闻推送成功！请检查您的微信"
            }), 200
        else:
            logger.error("新闻推送失败")
            return jsonify({
                "status": "failed",
                "message": "新闻推送失败"
            }), 500

    except Exception as e:
        logger.error(f"触发新闻推送异常: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/preview')
def preview_news():
    """预览新闻内容（不发送）"""
    try:
        fetcher = NewsFetcher(Config.NEWS_SOURCES)
        all_news = fetcher.fetch_all_news()

        # 生成HTML预览
        html = "<h1>今日新闻预览</h1>"

        for category, news_list in all_news.items():
            html += f"<h2>{category} ({len(news_list)}条)</h2>"
            for i, news in enumerate(news_list, 1):
                html += f"<h3>{i}. {news['title']}</h3>"
                html += f"<p><strong>来源:</strong> {news['source']}</p>"
                html += f"<p><strong>摘要:</strong> {news['summary']}</p>"
                html += f"<p><a href='{news['link']}'>阅读全文</a></p>"
                html += "<hr>"

        return html

    except Exception as e:
        return f"<h1>错误</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    logger.info("启动新闻聚合服务...")
    logger.info("访问 http://localhost:5002 查看控制面板")
    logger.info("访问 http://localhost:5002/preview 预览新闻")
    logger.info("访问 http://localhost:5002/trigger 触发推送")

    app.run(host='0.0.0.0', port=5002, debug=False)
