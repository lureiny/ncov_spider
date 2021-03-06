import pymongo
from pymongo import MongoClient
from units import print_info


class MongoDB():
    def __init__(self, url, collection):
        super().__init__()
        self.url = url
        self.collection = collection
        self.__connction__()

    def __connction__(self):
        self.db = MongoClient(self.url).ncov
        self.__collection = self.db[self.collection]

    def insert(self, document):
        try:
            self.__collection.insert_one(document)
            return True
        except pymongo.errors.DuplicateKeyError:
            # print_info("ID重复")
            print_info("ID重复：{}".format(str(document)))
            return False
        except Exception:
            print_info("其他错误：{}".format(str(document)))
            return False

