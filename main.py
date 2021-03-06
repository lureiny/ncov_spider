from setting import SPIDERS, SLEEP_TIME, LOG
import time
from units import print_info, update_redis
import sys

sys.stdout = open(LOG, "a")

if __name__ == '__main__':
    # 初始化去重队列
    update_redis()
    Spiders = __import__("spider")
    num = 1
    while True:
        if len(SPIDERS) == 0:
            print_info("未指定爬虫，程序退出")
            break
        for spider in SPIDERS:
            print_info("{}开始第{}次运行".format(spider, num))
            spider_class = getattr(Spiders, spider)
            spider_object = spider_class()
            spider_object.spider()
            print_info("{}第{}次运行结束".format(spider, num))
        num += 1
        time.sleep(SLEEP_TIME)
