import requests
from lxml import etree
from units import print_info
from setting import HEADERS

class Download():
    def __init__(self, url):
        super().__init__()
        self.url = url

    # 如果需要设计自己的下载类，可以重载此函数
    def request(self):
        try:
            resp = requests.get(url = self.url, headers=HEADERS)
            root = etree.HTML(resp.content.decode("utf-8"))
        except Exception as error:
            print_info("{} 下载失败，错误信息：{}".format(self.url, error.__str__()))
            root = False
        return root