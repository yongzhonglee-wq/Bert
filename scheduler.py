from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks import fetch_and_send_news
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsScheduler:
    """新闻推送定时任务调度器"""

    def __init__(self):
        self.scheduler = None

    def start(self):
        """启动调度器"""
        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

        # 解析cron表达式
        cron_expr = Config.CRON_SCHEDULE  # "30 8 * * *" 每天早上8:30
        parts = cron_expr.split()
        if len(parts) != 5:
            logger.error(f"无效的cron表达式: {cron_expr}")
            raise ValueError("无效的cron表达式")

        minute, hour, day, month, day_of_week = parts

        # 添加定时任务
        self.scheduler.add_job(
            func=fetch_and_send_news.delay,
            trigger=CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            ),
            id='news_push_task',
            name='每日新闻推送',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"定时任务调度器已启动，执行时间: {cron_expr}")

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")


# 全局调度器实例
scheduler = NewsScheduler()
