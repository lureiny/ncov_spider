from mongodb import MongoDB
import redis
from setting import MONGODB_URI

class Item():
    # 定义字段名
    def __init__(self):
        super().__init__()
        self._info = dict()        # Item的信息
    
    # 更新存储对象类信息
    def set_info(self, info):
        """
        更新信息，
        """
        self._info.update(info)  
    
    # 使用key获取存储对象的某个属性
    def get_info(self, key):
        if key in self._info:
            return self._info[key]     
        else:
            return False 

    # 存储对象信息处理
    def deal(self):
        mongo = MongoDB(MONGODB_URI, "notices")
        mongo.insert(self._info)

    def __str__(self):
        return str(self._info)


class GDWJWItem(Item):
    def __init__(self):
        super().__init__()
        self._info = {
            "_id": "",
            "title": "",
            "sourceUrl": "",
            "agency": "",
            "date": "",
            "source": "",
            "body": [],
            "effective": False
        }
    
    # 存储对象信息处理
    def deal(self):
        mongo = MongoDB(MONGODB_URI, "notices")
        del self._info["effective"]
        mongo.insert(self._info)