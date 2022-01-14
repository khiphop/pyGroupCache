# coding: utf-8
import threading
import time
import hashlib
import requests
import json
import copy

from Step3.cac import Cac


def do_http(url):
    """
    此处阻塞请求, 需要优化 / need perf: it's a block request
    """
    try:
        r = requests.post(url=url, timeout=0.2)
        d = json.loads(r.content)
    except BaseException as err:
        d = ''

    return d


def get_back_source_gk(group, key):
    return hashlib.md5(group.encode(encoding='UTF-8')).hexdigest() \
                     + '-' + hashlib.md5(key.encode(encoding='UTF-8')).hexdigest()


class Group:
    def __init__(self, groups):
        self.back_source = {}
        self.back_source_gk = {}
        self.back_source_cd = 60
        self.mu_map = {}

        self.struct = {
            'map': {}
        }

        for i in range(len(groups)):
            g = groups[i]
            group_name = g['name']
            self.struct['map'][group_name] = g['operator']
            self.back_source[group_name] = g['back_source']
            self.mu_map[group_name] = threading.Lock()

    def gp_get(self, group, key):
        group = str(group)
        if group not in self.struct['map']:
            return ''

        val = self.struct['map'][group].get_cache(key)

        # 触发回源 / trigger back-source
        if not val:
            print('Trigger back-source')
            self.mu_map[group].acquire()

            print('back-source ing:', key)
            print('back-source ing:', key)
            print('back-source ing:', key)

            val = self.on_back_source(group, key)

            if val:
                self.struct['map'][group].set_cache(key, val)

            self.mu_map[group].release()

        return val

    def gp_set(self, group, key, val):
        group = str(group)
        if group not in self.struct['map']:
            return False

        r = self.struct['map'][group].set_cache(key, val)

        return r

    def on_back_source(self, group, key):
        # 复检数据是否存在 / recheck if val exists
        val = self.struct['map'][group].get_cache(key)

        if val:
            print('Recheck if val exists')

            return val

        # 回源cd / back-source cool down
        gk_key = get_back_source_gk(group, key)
        if gk_key in self.back_source_gk and int(self.back_source_gk[gk_key]) > int(time.time()):
            print('Back-source cd')

            return ''

        # 回源开始 / indeed start back source
        print('Indeed start back source')

        fetch_field = self.back_source[group]['field']

        # Async http request
        url = self.back_source[group]['url']
        url = url + '?group=' + str(group) + '&key=' + key
        resp = do_http(url)

        # Update back-source cool down
        self.back_source_gk[gk_key] = int(time.time()) + self.back_source_cd

        if not resp:
            return ''

        fields = fetch_field.split('.')
        r = ''

        try:
            for i in range(len(fields)):
                if i == 0:
                    r = resp[fields[i]]
                else:
                    r = r[fields[i]]
        except BaseException as err:
            pass

        return r

    def copy_data(self):

        ll = []
        dt = {}
        for g in self.struct['map']:
            self.mu_map[g].acquire()

            if len(self.struct['map'][g].lru.struct['list']) == 0:
                continue

            ll.append(copy.deepcopy({'g': g, 'd': self.struct['map'][g].lru.struct['list']}))
            # dt.append(copy.deepcopy({'g': g, 'd': self.struct['map'][g].lru.struct['dict']}))
            dt[g] = copy.deepcopy(self.struct['map'][g].lru.struct['dict'])

            self.mu_map[g].release()

        return ll, dt


def new_groups():
    rules = [
        {
            'name': 'club',
            'size': 1 << 9,
            'ttl': 172800,
            'back_source': {
                'url': 'http://127.0.0.1:8013',
                'field': 'data',
            },
        },
        {
            'name': 'user',
            'size': 1 << 20,
            'ttl': 172800,
            'back_source': {
                'url': 'http://127.0.0.1:8001',
                'field': 'data.version',
            },
        },
    ]

    groups = []
    for i in range(len(rules)):
        g = rules[i]
        groups.append({
            'name': g['name'],
            'operator': Cac(g['size'], g['ttl'], 0),
            'back_source': g['back_source'],
        })

    return Group(groups)


def demo_set_get():
    groupCache = new_groups()
    groupCache.gp_set('user', 'kevin', 'age:30')
    val = groupCache.gp_get('user', 'kevin')
    print('1st ', val)

    val = groupCache.gp_get('room', 'kevin')
    print('2nd ', val)


def demo_on_back_source():
    groupCache = new_groups()
    val = groupCache.gp_get('user', 'kevin')
    print('1st ', val)


def demo_back_source_mutex():
    groupCache = new_groups()

    threads = []
    for i in range(20):
        t = threading.Thread(target=groupCache.gp_get, args=('user', str(i)))
        threads.append(t)

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    val = groupCache.gp_get('user', '1')
    print('1st ', val)


def demo_back_source_recheck():
    groupCache = new_groups()

    threads = []
    for i in range(20):
        t = threading.Thread(target=groupCache.gp_get, args=('user', 'kevin'))
        threads.append(t)

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    val = groupCache.gp_get('user', 'kevin')
    print('kevin: ', val)


def demo_back_source_cd():
    groupCache = new_groups()

    threads = []
    for i in range(20):
        t = threading.Thread(target=groupCache.gp_get, args=('club', 'kevin'))
        threads.append(t)

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    val = groupCache.gp_get('club', 'kevin')
    print('kevin: ', val)


if __name__ == '__main__':
    # demo_set_get()
    # demo_on_back_source()
    # demo_back_source_mutex()
    # demo_back_source_recheck()
    demo_back_source_cd()
