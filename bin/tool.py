#! /usr/bin/env python
import json
import sys

from plowshare import Plowshare

if __name__ == "__main__":
    filename    = sys.argv[1]
    host_number = int(sys.argv[2])

    result = Plowshare().upload(filename, host_number)

    print json.dumps(result)
