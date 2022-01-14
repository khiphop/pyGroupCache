# coding: utf-8
import sys
import time
import datetime


class Lru:
    def __init__(self, max_size, c=0, ttl=0, remover=None):
        self.struct = {
            'max_size': max_size,  # 单位: 字节 / byte
            'capacity': c,
            'used_size': 0,  # 单位: 字节 /byte
            'current_count': 0,
            'list': [],  # 存 [key] / storage key
            'dict': {},  # 存 {key: val} / storage {key: val}
            'ttl': int(ttl),
            'on_remove': remover,
        }

    def check_size(self):
        """
        python的dict释放不了内存, 有内存泄露的问题
        """
        while 0 < self.struct['max_size'] < self.struct['used_size']:
            self.lru_remove_one()
            self.update_memory_usage()

            # dict键值对的内存释放不了
            break

        while 0 < self.struct['capacity'] < len(self.struct['list']):
            self.lru_remove_one()

    def lru_remove_one(self):
        if len(self.struct['list']) == 0:
            return False

        key = self.struct['list'].pop(-1)
        self.struct['dict'].pop(key)

        if self.struct['on_remove']:
            (self.struct['on_remove'])(key)

        return True

    def lru_set(self, key, val):
        if key in self.struct['dict']:
            self.move_2_head(key)
        else:
            self.struct['list'].insert(0, key)

        self.struct['dict'][key] = {
            'val': val,
            'exp': int(time.time()) + self.struct['ttl'] if self.struct['ttl'] > 0 else 0,
        }

        self.update_memory_usage()

        self.check_size()

        return True

    def lru_get(self, key):
        if key not in self.struct['dict']:
            return ''

        d = self.struct['dict'][key]

        if 'exp' in d:
            if 0 < d['exp'] < time.time():
                self.expire(key)
                self.update_memory_usage()
                return ''

        self.move_2_head(key)

        return d['val']

    def expire(self, key):
        print("Trigger expire")

        if len(self.struct['list']) == 0:
            return False

        self.struct['list'].remove(key)
        self.struct['dict'].pop(key)

        return True

    def update_memory_usage(self):
        self.struct['used_size'] = int(sys.getsizeof(self.struct['list'])) + int(sys.getsizeof(self.struct['dict']))
        # print('memory_usage: ' + str(self.struct['used_size']))

    def update_current_count(self):
        self.struct['current_count'] = len(self.struct['list'])

    def move_2_head(self, key):
        self.struct['list'].pop(self.struct['list'].index(key))
        self.struct['list'].insert(0, key)

    def on_remove(self, key):
        pass


def demo_set_get():
    """
    cn: 演示设置一个键值对并查询该键的值
    en: demo set a key:val and get it
    """
    lru = Lru(1 << 20, 10, 0)

    val = lru.lru_get('kevin')
    print('1st get: ', val)

    lru.lru_set('kevin', 'age:30')
    val = lru.lru_get('kevin')
    print('2nd get: ', val)


def demo_move_2_head():
    """
    cn: 演示 LRU 算法对列表顺序的影响
    en: Demo how LRU effects the order of list
    """
    lru = Lru(1 << 20, 10, 0)
    lru.lru_set('kevin', 'age:30')
    lru.lru_set('allen', 'age:25')
    lru.lru_set('candy', 'age:19')

    print(lru.struct['list'], "\n")

    print('Do set bruce')
    lru.lru_set('bruce', 'age:22')
    print(lru.struct['list'], "\n")

    print('Do set candy')
    lru.lru_set('candy', 'age:19')
    print(lru.struct['list'], "\n")

    print('Do get allen')
    lru.lru_get('allen')
    print(lru.struct['list'], "\n")


def demo_on_remove():
    lru = Lru(1 << 20, 3, 0)

    lru.lru_set('kevin', 'age:30')
    lru.lru_set('allen', 'age:25')
    lru.lru_set('candy', 'age:19')

    print(lru.struct['list'], "\n")

    print('Do set bruce')
    lru.lru_set('bruce', 'age:22')
    print(lru.struct['list'], "\n")


# remover defined by you
def on_remove(key):
    print('on_remove')
    log_file = './onRemove.txt'
    file_handle = open(log_file, mode='a')
    file_handle.write((datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S') + ' | ' + key + '\n')


def demo_custom_on_remove():
    lru = Lru(1 << 20, 3, 0, on_remove)

    lru.lru_set('kevin', 'age:30')
    lru.lru_set('allen', 'age:25')
    lru.lru_set('candy', 'age:19')

    print(lru.struct['list'], "\n")

    print('Do set bruce')
    lru.lru_set('bruce', 'age:22')
    print(lru.struct['list'], "\n")


def demo_on_expire():
    lru = Lru(1 << 20, 30, 2)

    lru.lru_set('kevin', 'age:30')
    time.sleep(1)
    lru.lru_set('allen', 'age:25')
    time.sleep(1)  # annotation at 2nd time

    val = lru.lru_get('kevin')
    print("kevin:", val)
    print(lru.struct['list'], "\n")


if __name__ == '__main__':
    # demo_set_get()
    demo_move_2_head()
    # demo_on_remove()
    # demo_custom_on_remove()
    # demo_on_expire()
