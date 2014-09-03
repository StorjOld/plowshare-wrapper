import subprocess
import random
import os

# Same as multiprocessing, but thread only.
# We don't need to spawn new processes for this.
import multiprocessing.dummy

import hosts


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
        return self.multiupload(filename, self.random_hosts(number_of_hosts))


    def download(self, uploads, output_directory, filename):
        """Download a file from one of the provided sources."""

        upload = self.random_upload(uploads)
        if upload == None:
            return { "error": "no valid uploads" }

        try:
            filename = self.download_from_host(
                upload,
                output_directory,
                filename)

            return { "path": filename }

        except subprocess.CalledProcessError:
            return { "error": "plowshare error" }


    def download_from_host(self, upload, output_directory, filename):
        """Download a file from a given host.

        This method renames the file to the given string.

        """
        output = subprocess.check_output(
            ["plowdown", upload["url"], "-o", output_directory, "--temp-rename"],
            stderr=open("/dev/null", "w"))

        temporary_filename = self.parse_output(upload["host_name"], output)
        final_filename     = os.path.join(output_directory, filename)

        os.rename(temporary_filename, final_filename)

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
        """Parse plowup's output.

        For now, we just return the last line.

        """
        return output.split()[-1]


    def random_upload(self, uploads):
        """Select a random valid upload."""
        valid_uploads = [
            upload
            for upload in uploads
            if "error" not in upload]

        if len(valid_uploads) == 0:
            return None

        return random.choice(valid_uploads)
