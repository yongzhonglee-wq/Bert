# 新闻聚合应用

定时获取科技、军事、体育类新闻，并推送到微信。

## 功能特性

- 自动获取科技、军事、体育类新闻
- 筛选热门高质量新闻
- 每天早上8:30定时推送到微信
- 支持手动触发推送

## 部署方式

### 使用Docker Compose（推荐）

```bash
# 1. 复制环境变量文件
cp .env.example .env

# 2. 修改.env文件中的配置（微信AppID、AppSecret、OpenID等）

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 手动触发测试

```bash
# 发送POST请求触发新闻推送
curl -X POST http://localhost:5000/trigger

# 查看任务状态
curl http://localhost:5000/task/<task_id>
```

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
# 微信公众号配置
WECHAT_APPID=your_appid
WECHAT_APPSECRET=your_appsecret
WECHAT_OPENID=your_openid
WECHAT_TEMPLATE_ID=

# 数据库配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=news_aggregator
DB_USER=news_user
DB_PASSWORD=news_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# 定时任务配置
CRON_SCHEDULE=30 8 * * *

# 新闻配置
NEWS_PER_CATEGORY=5
ENABLE_SUMMARY=true
```

### 调整推送时间

修改 `CRON_SCHEDULE` 环境变量，格式为 `分 时 日 月 周`：

- `30 8 * * *` - 每天早上8:30
- `0 9 * * *` - 每天早上9:00
- `30 8 * * 1-5` - 周一到周五早上8:30

## 项目结构

```
.
├── app.py                 # Flask应用入口
├── config.py              # 配置文件
├── routes.py              # API路由
├── tasks.py               # Celery异步任务
├── news_fetcher.py        # 新闻获取模块
├── wechat_notifier.py     # 微信推送模块
├── scheduler.py           # 定时任务调度器
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置
└── .env.example          # 环境变量示例
```

## API接口

- `GET /health` - 健康检查
- `POST /trigger` - 手动触发新闻推送
- `GET /task/<task_id>` - 查看任务状态

## 常见问题

### 如何获取微信OpenID？

1. 访问微信公众号测试号管理页面
2. 扫描测试号二维码关注
3. 在页面下方的"接口配置信息"中找到"接口配置信息"
4. 或使用调试工具获取用户基本信息

### 如何创建微信模板消息？

应用会自动尝试创建模板消息，如果失败可以：
1. 访问微信公众号测试号管理页面
2. 在"模板消息接口"中手动创建模板
3. 将模板ID填入 `.env` 文件

### 如何查看推送日志？

```bash
# 查看所有容器日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f celery-worker
docker-compose logs -f web
```

## License

MIT
