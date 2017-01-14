#! /usr/bin/python
from gluster import gfapi


if __name__ == '__main__':
    bytes = bytearray([5 for i in xrange(2 ** 28)])


    vol = gfapi.Volume(host='node150', volname='vol1')
    ret = vol.mount()
    with vol.fopen('test.txt', 'w+') as f:
        f.write(bytes)
        f.fsync()
