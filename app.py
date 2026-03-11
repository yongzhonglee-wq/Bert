from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes import bp
    app.register_blueprint(bp)

    # 启动调度器
    try:
        from scheduler import scheduler
        scheduler.start()
        print("定时任务调度器已启动")
    except Exception as e:
        print(f"启动调度器失败: {e}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
