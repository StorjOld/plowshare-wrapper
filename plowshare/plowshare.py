import subprocess
import random
import time
import hashlib
import os

# Same as multiprocessing, but thread only.
# We don't need to spawn new processes for this.
import multiprocessing.dummy

import hosts


def sha256(path):
    """Return the sha256 digest of the file located at the specified path."""
    h = hashlib.sha256()
    with open(path) as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)

    return h.hexdigest()


class Plowshare(object):
    """Upload and download files using the plowshare tool.

    """
    def __init__(self, host_list = hosts.anonymous):
        self.hosts = host_list

    def random_hosts(self, number_of_hosts):
        """Retrieve a random subset of available hosts.

        The number of hosts provided must not be larger
        than the number of available of hosts, otherwise
        it will throw a ValueError exception.
        """
        return random.sample(self.hosts, number_of_hosts)

    def upload(self, filename, number_of_hosts):
        """Upload the given file to the specified number of hosts."""
        results = self.multiupload(filename, self.random_hosts(number_of_hosts))

        return {
            "version":  "0.1",
            "datetime": str(int(time.time())),
            "filesize": str(os.path.getsize(filename)),
            "filehash": sha256(filename),
            "uploads":  results
        }

    def download(self, info, output_directory):
        if info["version"] != "0.1":
            return { "error": "unsupported format" }

        upload = self.arbitrary_valid_upload(info)
        if upload == None:
            return { "error": "no valid uploads" }

        filename = ""
        try:
            filename = self.download_from_host(
                upload,
                info["filehash"],
                output_directory)
        except subprocess.CalledProcessError:
            return { "error": "plowshare error" }

        if info["filesize"] != str(os.path.getsize(filename)):
            return { "error": "file sizes mismatch" }

        if info["filehash"] != sha256(filename):
            return { "error": "file hashes mismatch" }

        return { "path": filename }

    def download_from_host(self, upload, filehash, output_directory):
        """Download a file from a given host.

        This method renames the file so the hash is part of its name.

        """
        output = subprocess.check_output(
            ["plowdown", upload["url"], "-o", output_directory, "--temp-rename"],
            stderr=open("/dev/null", "w"))

        filename = self.parse_output(upload["host_name"], output)

        final_filename = "{0}/{1}_{2}".format(
            output_directory,
            filehash[:7],
            os.path.basename(filename))

        os.rename(filename, final_filename)

        return final_filename


    def multiupload(self, filename, hosts):
        """Upload filename to multiple hosts simultaneously."""
        def f(host):
            return self.upload_to_host(filename, host)

        return multiprocessing.dummy.Pool(len(hosts)).map(f, hosts)

    def upload_to_host(self, filename, hostname):
        """Upload a file to the given host.

        This method relies on 'plowup' being installed on the system.
        If it succeeds, this method returns a dictionary with the host name,
        and the final URL. Otherwise, it returns a dictionary with the
        host name and an error flag.

        """
        try:
            output = subprocess.check_output(
                ["plowup", hostname, filename],
                stderr=open("/dev/null", "w"))

            output = self.parse_output(hostname, output)
            return { "host_name": hostname, "url": output }

        except subprocess.CalledProcessError:
            return { "host_name": hostname, "error": True }

    def parse_output(self, hostname, output):
        """Parse plowup's output. For now, we just return the last line."""
        return output.split()[-1]

    def arbitrary_valid_upload(self, info):
        valid_uploads = [
            upload
            for upload in info["uploads"]
            if "error" not in upload]

        if len(valid_uploads) == 0:
            return None

        return valid_uploads[0]
