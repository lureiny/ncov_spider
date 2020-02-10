import time
from setting import REDIS_HOST, REDIS_PORT, INIT_LIST, FILTER_QUEUE
import redis


def print_info(info):
    print(time.ctime(), end="", flush=True)
    print(": ", end="", flush=True)
    print(info, flush=True)


def update_redis():
    r_c = redis.Redis(REDIS_HOST, REDIS_PORT, db=0)
    for u in INIT_LIST:
        r_c.sadd(FILTER_QUEUE, u)


if __name__ == '__main__':
    update_redis()
