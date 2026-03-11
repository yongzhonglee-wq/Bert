from celery import Celery
from news_fetcher import NewsFetcher
from wechat_notifier import WeChatNotifier
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Celery实例
celery = Celery('news_tasks')
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
)


@celery.task(name='tasks.fetch_and_send_news')
def fetch_and_send_news():
    """获取并发送新闻任务"""
    logger.info("开始执行新闻推送任务...")

    try:
        # 初始化新闻获取器
        fetcher = NewsFetcher(Config.NEWS_SOURCES)

        # 获取所有分类的新闻
        all_news = fetcher.fetch_all_news()

        if not all_news:
            logger.warning("没有获取到任何新闻")
            return {"status": "failed", "message": "没有获取到任何新闻"}

        # 初始化微信推送器
        notifier = WeChatNotifier()

        # 发送微信推送
        success = notifier.send_news_notification(all_news)

        if success:
            logger.info("新闻推送任务执行成功")
            return {"status": "success", "message": "新闻推送成功"}
        else:
            logger.error("新闻推送任务执行失败")
            return {"status": "failed", "message": "新闻推送失败"}

    except Exception as e:
        logger.error(f"新闻推送任务执行异常: {e}")
        return {"status": "failed", "message": str(e)}


@celery.task(name='tasks.manual_trigger')
def manual_trigger():
    """手动触发新闻推送"""
    logger.info("手动触发新闻推送任务...")
    return fetch_and_send_news()
