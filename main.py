from setting import SPIDERS, SLEEP_TIME
import time
from units import print_info

if __name__ == '__main__':
    Spiders = __import__("spider")
    num = 1
    while True:
        if len(SPIDERS) == 0:
            print_info("未指定爬虫，程序退出")
            break
        for spider in SPIDERS:
            spider_class = getattr(Spiders, spider)
            spider = spider_class()
            spider.spider()
        print_info("第{}次爬虫运行结束".format(num))
        num += 1
        time.sleep(SLEEP_TIME)
