import plowshare
import json
import sys

if __name__ == "__main__":
    filename    = sys.argv[1]
    host_number = int(sys.argv[2])
    config_name = sys.argv[3]

    result = plowshare.Plowshare(config_name).upload(filename, host_number)

    print json.dumps(result)
