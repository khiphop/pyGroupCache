# coding:utf-8

from app.util.con_hash import ConHash

if __name__ == "__main__":
    Ch = ConHash(5)
    Ch.add_nodes(['127.0.0.1:1111', '127.0.0.1:2222', '127.0.0.1:3333', '127.0.0.1:4444'])
    print(Ch.hash_ring)
    print(Ch.hash_ring_map)

    for i in range(10):
        node = Ch.choose_node('kevin' + str(i))
        print('kevin' + str(i) + ' : ' + node)

    Ch.remove_nodes(['127.0.0.1:1111'])
    print('---------------')

    for i in range(10):
        node = Ch.choose_node('kevin' + str(i))
        print('kevin' + str(i) + ' : ' + node)

    Ch.add_nodes(['127.0.0.1:5555'])
    print('---------------')

    for i in range(10):
        node = Ch.choose_node('kevin' + str(i))
        print('kevin' + str(i) + ' : ' + node)

    # print(Ch.choose_node('allen'))
