#! /usr/bin/env python

import plowshare
import json
import sys

if __name__ == "__main__":
    filename    = sys.argv[1]
    host_number = int(sys.argv[2])

    result = plowshare.Plowshare().upload(filename, host_number)

    print json.dumps(result)
