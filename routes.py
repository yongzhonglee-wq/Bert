from flask import Blueprint, jsonify, request
from tasks import fetch_and_send_news, manual_trigger, celery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "message": "News Aggregator is running"
    })


@bp.route('/trigger', methods=['POST'])
def trigger_news():
    """手动触发新闻推送"""
    try:
        result = manual_trigger.delay()
        return jsonify({
            "status": "success",
            "message": "新闻推送任务已触发",
            "task_id": result.id
        }), 200
    except Exception as e:
        logger.error(f"触发新闻推送失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    try:
        result = celery.AsyncResult(task_id)
        return jsonify({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }), 200
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
