import requests
from lxml import etree
from units import print_info

class Download():
    def __init__(self, url):
        super().__init__()
        self.url = url

    def request(self):
        try:
            resp = requests.get(url = self.url)
            root = etree.HTML(resp.text)
        except Exception as error:
            print_info("{}爬取失败，错误信息：{}".format(url, error.__str__()))
            root = False
        return root