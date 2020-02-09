# Redis配置信息
REDIS_HOST = "ncov_spider_redis"
REDIS_PORT = 6379

# 数据库存储配置，这里使用MongoDB作为演示
MONGODB_URI = "mongodb://user:passwd@ncov_spider_mongo:27017/?authSource=ncov"

# URL队列信息
FILTER_QUEUE = "FILTER"

# 爬虫列表，对象为Spider类的子类
SPIDERS = ["RumorSpider", "SZWJWSpider", "GDWJWSpider"]

# 爬虫间隔时间，单位：秒
SLEEP_TIME = 600

# 请求头
HEADERS = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}

# 日志文件地址
LOG = "/usr/src/ncov_spider/spider.log"