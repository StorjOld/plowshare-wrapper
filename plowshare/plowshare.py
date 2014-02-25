import subprocess

import random
import json
import time
import hashlib
import os


def sha256(path):
    """Return the sha256 digest of the file located at the specified path."""
    h = hashlib.sha256()
    with open(path) as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)

    return h.hexdigest()


class Config(object):
    """Manage the plowshare wrapper configuration.

    Given the path to the configuration file, this
    class handles all configuration parsing and exposes
    it as a python object.

    Currently, this file is composed of only a list
    of plowshare modules to use.

    """
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.host_list = f.read().split()

    def hosts(self):
        """Return the list of available host names."""
        return self.host_list


class Plowshare(object):
    def __init__(self, config_filename):
        self.cfg = Config(config_filename)

    def random_hosts(self, number_of_hosts):
        return random.sample(self.cfg.hosts(), number_of_hosts)

    def upload(self, filename, number_of_hosts):
        results = [
            self.upload_to_host(filename, hostname)
            for hostname
            in self.random_hosts(number_of_hosts)]

        return {
            "version":  "0.1",
            "datetime": str(int(time.time())),
            "filesize": str(os.path.getsize(filename)),
            "filehash": sha256(filename),
            "uploads":  results
        }

    def parse_output(self, hostname, output):
        return output.split()[-1]

    def upload_to_host(self, filename, hostname):
        output = ""

        try:
            output = subprocess.check_output(
                ["plowup", hostname, filename],
                stderr=open("/dev/null", "w"))

            output = self.parse_output(hostname, output)

        except subprocess.CalledProcessError:
            output = "error"

        return { "host_name": hostname, "url": output }
