#!/usr/bin/env python3

import hashlib
import sys
import requests


def main(name, version):
    tarball = 'https://pypi.io/packages/source/{0}/{1}/{1}-{2}.tar.gz'.format(name[0], name, version)
    print('Tarball: {!r}'.format(tarball))
    r = requests.get(tarball)

    r.raise_for_status()
    sha1 = hashlib.sha256(r.content).hexdigest()
    print(sha1)
    return sha1


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
