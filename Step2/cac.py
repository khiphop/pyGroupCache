# coding: utf-8
import threading
import time

from pyCache.app.util.lru import Lru


def handle_set_val(val):
    return bytes(str(val), encoding='utf8')


def handle_get_val(byte_val):
    if not byte_val:
        return ''

    return byte_val.decode()


class Cac:
    def __init__(self, max_size, c=0, ttl=0, remover=None):
        self.mutex = threading.Lock()
        self.lru = Lru(max_size, c, ttl, remover)

    def get_cache(self, key):
        key = str(key)
        self.mutex.acquire()

        r = self.lru.lru_get(key)
        self.mutex.release()

        return handle_get_val(r)

    def set_cache(self, key, val):
        self.mutex.acquire()

        # print('--------', key)
        # time.sleep(0.01)
        # print('--------', key)
        # print('--------', key)
        # print()

        r = self.lru.lru_set(key, handle_set_val(val))

        self.mutex.release()

        return r


def demo_set_get():
    cache = Cac(1 << 20, 0, 0)
    cache.set_cache('kevin', 'age:30')
    val = cache.get_cache('kevin')
    print(val)


def demo_mutex_lock():
    cache = Cac(1 << 20, 0, 0)

    threads = []
    for i in range(20):
        t = threading.Thread(target=Cac.set_cache, args=(cache, str(i), str(i)))
        threads.append(t)

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    val = cache.get_cache('1')
    print(val)


if __name__ == '__main__':
    # demo_set_get()
    demo_mutex_lock()
