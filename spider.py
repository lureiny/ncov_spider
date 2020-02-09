from download import Download
import re
from item import GDWJWItem, SZWJWItem
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
                item.set_info({"title": a.get("title"), "sourceUrl": a.get("href"), "_id": generate_hash("{}{}".format(a.get("title"), span.text)), "agency": "广东省卫健委", "date": span.text, "effective": True})
                items.append(item)

    # 获取单个文章信息
    def get_post(self, item):
        xml = Download(item.get_info("sourceUrl")).request()
        if xml is not False:
            try:
                source_date = xml.xpath('//p[@class="margin_top15 c999999 text_cencer"]')[0].text
            except Exception:
                print_info("{} 解析失败".format(item.get_info("sourceUrl")))
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

class SZWJWSpider(GDWJWSpider):
    def __init__(self):
        self._start_url = "http://wjw.sz.gov.cn/yqxx/index.htm"
        self._page_num = self.get_page_num()

    # 获取页数
    def get_page_num(self):
        xml = Download(self._start_url).request()
        js_func = xml.xpath('//div[@class="zx_ml_list_page"]/script/text()')[0]
        js_func = js_func.replace("createPageHTML(", "").replace(");", "")
        return int(js_func.split(",")[0])

    # 获取文章列表
    def get_post_list(self, url, items):
        xml = Download(url).request()
        lis = xml.xpath('//div[@class="wendangListC"][1]//li')
        for li in lis:
            date = li.find("strong").text
            a = li.find("a")
            post_url = re.sub("^\.", "http://wjw.sz.gov.cn/yqxx", a.get("href"))
            if self.url_repeat(post_url) is False:
                item = SZWJWItem()
                item.set_info({"title": a.text, "sourceUrl": post_url, "_id": generate_hash("{}{}".format(a.text, date)), "agency": "深圳卫健委", "date": date, "effective": True, "source": "深圳市卫生健康委员会"})
                items.append(item)

    # 获取单个文章
    def get_post(self, item):
        if item.get_info("sourceUrl").split(".")[-1] == "pdf":
            return
        xml = Download(item.get_info("sourceUrl")).request()
        if xml is not False:
            try:
                source_date = xml.xpath('//div[@class="xxxq_text_tit"][1]/h6/span[2]')[0]
                source_date = ["深圳市卫生健康委员会", source_date.text.replace("发布日期：", "")]
            except Exception as e:
                print_info("{} 解析失败".format(item.get_info("sourceUrl")))
                return 
            body = []
            for p in xml.xpath('//div[@class="TRS_Editor"]/p'):
                if p.text:
                    body.append(p.text.split("。"))
                else:
                    continue
            date = source_date[1]
            update_info = {"date": date, "_id": generate_hash("{}{}".format(item.get_info("title"), date)) ,"source": source_date[0], "body": body, "effective": True}
            item.set_info(update_info)

    def spider(self):
        # 获取全部文章列表的链接
        urls = []
        urls.append(self._start_url)
        if self._page_num != 1:
            for n in range(1, self._page_num):
                urls.append("http://wjw.sz.gov.cn/yqxx/index_{}.htm".format(n))
        # 抓取内容
        items = []
        for url in urls:
            self.get_post_list(url=url, items=items)
        
        for item in items:
            self.get_post(item=item)
            self.deal_item(item)
