from mongodb import MongoDB
import redis
from setting import MONGODB_URI

class Item():
    # 定义字段名
    def __init__(self):
        super().__init__()
        self.__info = dict()        # Item的信息
    
    def set_info(self, info):
        """
        更新信息，
        """
        self.__info.update(info)  
    
    def get_info(self, key):
        if key in self.__info:
            return self.__info[key]     
        else:
            return False 

    def deal(self):
        mongo = MongoDB(MONGODB_URI, "notices")
        mongo.insert(self.__info)

    def __str__(self):
        return str(self.__info)


class GDWJWItem(Item):
    def __init__(self):
        super().__init__()
        