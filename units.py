import time


def print_info(info):
    print(time.ctime(), end="", flush=True)
    print(": ", end="", flush=True)
    print(info, flush=True)