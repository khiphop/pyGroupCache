# coding: utf-8
from zlib import crc32
import threading


def str_2_hash(key):
    return abs(crc32(bytes(key, encoding="utf8")))


def handle_node(node):
    return node.split('-')[0]


def pkg_v_node_name(node, no):
    return str(node) + '-vn' + str(no)


class ConHash:
    def __init__(self, v_node_c):
        self.mutex = threading.Lock()

        self.hash_ring_map = {}
        self.hash_ring = []
        self.v_node_c = int(v_node_c)

    def add_nodes(self, nodes=None):
        if nodes is None:
            return False

        for i in range(len(nodes)):
            # add a real node
            self.do_add(nodes[i])
            for v in range(self.v_node_c):
                # add a virtual node
                self.do_add(pkg_v_node_name(nodes[i], v))

        self.hash_ring.sort()

        return self.hash_ring_map

    def do_add(self, node):
        self.mutex.acquire()

        node = str(node)
        nodeHash = str_2_hash(node)

        if nodeHash in self.hash_ring:
            pass
        else:
            self.hash_ring_map[nodeHash] = node
            self.hash_ring.append(nodeHash)

        self.mutex.release()

    def remove_nodes(self, nodes=None):
        if nodes is None:
            return False

        for node in nodes:
            self.do_remove(node)

            for v in range(self.v_node_c):
                self.do_remove(pkg_v_node_name(node, v))

        return self.hash_ring_map

    def do_remove(self, node):
        self.mutex.acquire()

        node = str(node)
        nodeHash = str_2_hash(node)

        self.hash_ring.remove(nodeHash)
        del self.hash_ring_map[nodeHash]

        self.mutex.release()

    def choose_node(self, key):
        self.mutex.acquire()

        keyHash = str_2_hash(key)
        node = self.hash_ring_map[self.hash_ring[0]]

        for nodeHash in self.hash_ring:
            if keyHash < nodeHash:
                node = self.hash_ring_map[nodeHash]
                break
            else:
                continue

        self.mutex.release()

        return handle_node(node)


def demo_simple():
    ch = ConHash(10)
    ch.add_nodes(['127.0.0.1:7000'])

    print(ch.hash_ring)
    print(ch.hash_ring_map)


def demo_choose_node():
    ch = ConHash(10)
    ch.add_nodes(['127.0.0.1:7000', '127.0.0.1:8000'])

    print(ch.hash_ring)
    print(ch.hash_ring_map)

    node = ch.choose_node('kevin')
    print('1st ', node)

    node = ch.choose_node('allen')
    print('2nd ', node)

    node = ch.choose_node('bruce')
    print('3rd ', node)


def demo_vnc_effect():
    ch = ConHash(10)
    ch.add_nodes(['127.0.0.1:7000', '127.0.0.1:8000', '127.0.0.1:9000'])

    total_times = 100
    res = {
        '127.0.0.1:7000': 0,
        '127.0.0.1:8000': 0,
        '127.0.0.1:9000': 0,
    }
    for i in range(total_times):
        node = ch.choose_node('node#'+str(i))
        res[node] += 1
    
    for node in res:
        print(node, ': ', str(int(100 * res[node] / total_times)))


if __name__ == '__main__':
    # demo_simple()
    # demo_choose_node()
    demo_vnc_effect()
