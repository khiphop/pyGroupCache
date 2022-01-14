# coding:utf-8

import socket
from zlib import crc32
from app.util.con_hash import ConHash

if __name__ == "__main__":
    Ch = ConHash(5)
    Ch.add_nodes(['127.0.0.1:8001', '127.0.0.1:8002', '127.0.0.1:3', '127.0.0.1:4', '127.0.0.1:5'])
    print(Ch.hash_ring)
    print(Ch.hash_ring_map)

    for i in range(10):
        print(Ch.choose_node('kevin' + str(i)))

    Ch.remove_nodes(['127.0.0.1:8001'])
    print('---------------')

    for i in range(10):
        print(Ch.choose_node('kevin' + str(i)))
    # print(Ch.choose_node('allen'))

