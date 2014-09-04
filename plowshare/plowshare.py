import os
import random
import subprocess

# Same as multiprocessing, but thread only.
# We don't need to spawn new processes for this.
import multiprocessing.dummy

from . import hosts


class Plowshare(object):
    """Upload and download files using the plowshare tool.

    """
    def __init__(self, host_list=hosts.anonymous):
        self.hosts = host_list

    def _run_command(self, command, **kwargs):
        try:
            return {'output': subprocess.check_output(command, **kwargs)}
        except Exception as e:
            return {'error': str(e)}

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


    def download(self, sources, output_directory, filename):
        """Download a file from one of the provided sources."""

        source = self.random_source(sources)
        if source is None:
            return {'error': 'no valid sources'}

        return self.download_from_host(source, output_directory, filename)


    def download_from_host(self, source, output_directory, filename):
        """Download a file from a given host.

        This method renames the file to the given string.

        """
        result = self._run_command(
            ["plowdown", source["url"], "-o", output_directory, "--temp-rename"],
            stderr=open("/dev/null", "w")
        )

        result['host_name'] = source['host_name']

        if 'error' in result:
            return result

        temporary_filename = self.parse_output(result['host_name'], result['output'])
        result['filename'] = os.path.join(output_directory, filename)
        result.pop('output')

        os.rename(temporary_filename, result['filename'])

        return result


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
        result = self._run_command(
            ["plowup", hostname, filename],
            stderr=open("/dev/null", "w")
        )

        result['host_name'] = hostname
        if 'error' not in result:
            result['url'] = self.parse_output(hostname, result.pop('output'))

        return result


    def parse_output(self, hostname, output):
        """Parse plowup's output.

        For now, we just return the last line.

        """
        return output.split()[-1]


    def random_source(self, sources):
        """Select a random valid source."""
        valid_sources = [
            source
            for source in sources
            if "error" not in source]

        if len(valid_sources) == 0:
            return None

        return random.choice(valid_sources)
