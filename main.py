from setting import SPIDERS, SLEEP_TIME
import time

if __name__ == '__main__':
    Spiders = __import__("spider")
    while True:
        if len(SPIDERS) == 0:
            print("未指定爬虫，程序退出")
            break
        for spider in SPIDERS:
            spider_class = getattr(Spiders, spider)
            spider = spider_class()
            spider.spider()
        time.sleep(SLEEP_TIME)
