# Redis配置信息
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

# 数据库存储配置，这里使用MongoDB作为演示
MONGODB_URI = "mongodb://user:pasword@127.0.0.1:27017/?authSource=db"

# URL队列信息
FILTER_QUEUE = "FILTER"

# 爬虫列表，对象为Spider类的子类
SPIDERS = []

# 爬虫间隔时间，单位：秒
SLEEP_TIME = 600
