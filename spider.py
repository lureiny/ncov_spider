from download import Download
import re
from item import GDWJWItem
import hashlib
from units import print_info
import redis
from setting import REDIS_HOST, REDIS_PORT, FILTER_QUEUE, MONGODB_URI

# runmors
import requests
from setting import HEADERS
from mongodb import MongoDB


def generate_hash(info):
    return hashlib.sha256(info.encode("utf-8")).hexdigest()


class Spider():
    def __init__(self):
        super().__init__()
        self._start_url = ""

    # 去重判断，如果url已经遍历返回True，否则返回False
    def url_repeat(self, url):
        r_c = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        return r_c.sismember(FILTER_QUEUE, url)

    # 更新过滤队列
    def update_filter_queue(self, url):
        r_c = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        r_c.sadd(FILTER_QUEUE, url)

    # 处理item，主要是进行存储等
    def deal_item(self, item):
        if item.deal():
            self.update_filter_queue(item.get_info("sourceUrl"))

    # 必须重载，执行爬虫操作
    def spider(self):
        pass


# 广东卫健卫爬虫，示例
class  GDWJWSpider(Spider):
    def __init__(self):
        super().__init__()
        self._start_url = "http://wsjkw.gd.gov.cn/xxgzbdfk/index.html"
        self._page_num = self.get_page_num()

    # 重载方法
    def deal_item(self, item):
        if item.get_info("effective") and item.deal():
            self.update_filter_queue(item.get_info("sourceUrl"))

    #  获取文章列表页数
    def get_page_num(self):
        xml = Download(self._start_url).request()
        if xml == False:
            return False
        last_url = xml.xpath('//a[@class="last"]')[0].xpath("@href")[0]
        html_names = re.findall(pattern=r"index_[\d]*.html", string=last_url)
        if len(html_names) >= 1:
            pages_num = int(html_names[0].replace("index_", "").replace(".html", ""))
            return pages_num
        else:
            return 1

    # 获取文章列表
    def get_post_list(self, url, items):
        xml = Download(url).request()
        lis = xml.xpath('//div[@class="section list"][1]/ul/li')
        for li in lis:
            a = li.find("a")
            span = li.find("span")
            if self.url_repeat(a.get("href")) is False:
                item = GDWJWItem()
                item.set_info({"title": a.get("title"), "sourceUrl": a.get("href"), "_id": generate_hash("{}{}".format(a.get("title"), span.text)), "agency": "广东省卫健委", "date": span.text})
                items.append(item)

    # 获取单个文章信息
    def get_post(self, item):
        xml = Download(item.get_info("sourceUrl")).request()
        try:
            source_date = xml.xpath('//p[@class="margin_top15 c999999 text_cencer"]')[0].text
        except IndexError:
            print_info("{}解析失败".format(item.get_info("sourceUrl")))
            item.set_info({"effective": True})
            return 
        except Exception:
            print_info("{}下载失败".format(item.get_info("sourceUrl")))
            return 
        source_date = source_date.split(" ")
        body = []
        for p in xml.xpath('//div[@class="content-content"]/p'):
            if p.text:
                body.append(p.text.split("。"))
        date = "{} {}".format(source_date[0].replace("时间：", ""), source_date[1])
        update_info = {"date": date, "_id": generate_hash("{}{}".format(item.get_info("title"), date)) ,"source": source_date[3].replace("来源：", ""), "body": body, "effective": True}
        item.set_info(update_info)

    # 爬虫主进程
    def spider(self):

        # 获取全部文章列表的链接
        urls = []
        urls.append(self._start_url)
        if self._page_num is False:
            return 
        elif self._page_num != 1:
            for n in range(2, self._page_num+1):
                urls.append("http://wsjkw.gd.gov.cn/xxgzbdfk/index_{}.html".format(n))
        # 抓取内容
        items = []
        for url in urls:
            self.get_post_list(url=url, items=items)

        for item in items:
            self.get_post(item)
            self.deal_item(item)


class RumorSpider(Spider):
    def __init__(self):
        super().__init__()

    # 获取谣言信息，来自丁香园
    def get_rumors(self, type):
        url = "https://lab.isaaclin.cn/nCoV/api/rumors?num=all&rumorType={}".format(type)
        resp = requests.get(url=url, headers=HEADERS)
        if resp.status_code != 200:
            print_info("Something Wrong, Status Code is: {}".format(resp.status_code))
            return False
        return resp.json()

    # 获取的数据存储到MongoDB
    def deal_item(self, data):
        rumors = data["results"]
        mongo = MongoDB(MONGODB_URI, "rumors")

        for rumor in rumors:
            rumor_id = generate_hash("{}{}".format(rumor["title"], rumor["rumorType"]))
            rumor.update({"_id": rumor_id})
            if self.url_repeat(rumor_id) is False and mongo.insert(rumor):
                self.update_filter_queue(rumor_id)

    def spider(self):
        for type in range(3):
            try:
                data = self.get_rumors(type=type)
                if data:
                    self.deal_item(data=data)
                else:
                    continue
            except Exception as error:
                print_info(error)
                continue
