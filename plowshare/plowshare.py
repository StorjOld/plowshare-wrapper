#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Storj Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import random
import subprocess
from collections import defaultdict

# Same as multiprocessing, but thread only.
# We don't need to spawn new processes for this.
import multiprocessing.dummy
from multiprocessing import Manager

from . import hosts
from . import settings


class Plowshare(object):

    """Upload and download files using the plowshare tool."""

    def __init__(self, host_list=hosts.anonymous):
        """Initialize Plowshare with the supplied hosts list.

        :param host_list: List of potential hosts to upload to.
        :type host_list: list
        """
        self.hosts = host_list
        self._host_errors = defaultdict(int)

    def _run_command(self, command, **kwargs):
        """Wrapper to pass command to plowshare.

        :param command: The command to pass to plowshare.
        :type command: str
        :param **kwargs: Additional keywords passed into
        :type **kwargs: dict
        :returns: Object containing either output of plowshare command or an
                  error message.
        :rtype: dict
        :raises: Exception
        """
        try:
            return {'output': subprocess.check_output(command, **kwargs)}
        except Exception as e:
            return {'error': str(e)}

    def _hosts_by_success(self, hosts=[]):
        """Order hosts by most successful (least amount of errors) first.

        :param hosts: List of hosts.
        :type hosts: list
        :returns: List of hosts sorted by successful connections.
        :rtype: list
        """
        hosts = hosts if hosts else self.hosts
        return sorted(hosts, key=lambda h: self._host_errors[h])

    def _filter_sources(self, sources):
        """Remove sources with errors and return ordered by host success.

        :param sources: List of potential sources to connect to.
        :type sources: list
        :returns: Sorted list of potential sources without errors.
        :rtype: list
        """
        filtered, hosts = [], []
        for source in sources:
            if 'error' in source:
                continue
            filtered.append(source)
            hosts.append(source['host_name'])

        return sorted(filtered, key=lambda s:
                      self._hosts_by_success(hosts).index(s['host_name']))

    def random_hosts(self, number_of_hosts):
        """Retrieve a random subset of available hosts.

        The number of hosts provided must not be larger
        than the number of available of hosts, otherwise
        it will throw a ValueError exception.

        :param number_of_hosts: Number of hosts to connect to.
        :type number_of_hosts: int
        :returns: Random subsample of available hosts.
        :rtype: list
        :raises: ValueError
        """
        return random.sample(self.hosts, number_of_hosts)

    def upload(self, filename, number_of_hosts):
        """Upload the given file to the specified number of hosts.

        :param filename: The filename of the file to upload.
        :type filename: str
        :param number_of_hosts: The number of hosts to connect to.
        :type number_of_hosts: int
        :returns:  A list of dicts with 'host_name' and 'url' keys for all
                   successful uploads or an empty list if all uploads failed.
        :rtype: list
        """
        return self.multiupload(filename, self.random_hosts(number_of_hosts))

    def download(self, sources, output_directory, filename):
        """Download a file from one of the provided sources

        The sources will be ordered by least amount of errors, so most
        successful hosts will be tried first. In case of failure, the next
        source will be attempted, until the first successful download is
        completed or all sources have been depleted.

        :param sources: A list of dicts with 'host_name' and 'url' keys.
        :type sources: list
        :param output_directory: Directory to save the downloaded file in.
        :type output_directory: str
        :param filename: Filename assigned to the downloaded file.
        :type filename: str
        :returns: A dict with 'host_name' and 'filename' keys if the download
                  is successful, or an empty dict otherwise.
        :rtype: dict
        """
        valid_sources = self._filter_sources(sources)
        if not valid_sources:
            return {'error': 'no valid sources'}

        manager = Manager()
        successful_downloads = manager.list([])

        def f(source):
            if not successful_downloads:
                result = self.download_from_host(
                    source, output_directory, filename)
                if 'error' in result:
                    self._host_errors[source['host_name']] += 1
                else:
                    successful_downloads.append(result)

        multiprocessing.dummy.Pool(len(valid_sources)).map(f, valid_sources)

        return successful_downloads[0] if successful_downloads else {}

    def download_from_host(self, source, output_directory, filename):
        """Download a file from a given host.

        This method renames the file to the given string.

        :param source: Dictionary containing information about host.
        :type source: dict
        :param output_directory: Directory to place output in.
        :type output_directory: str
        :param filename: The filename to rename to.
        :type filename: str
        :returns: Dictionary with information about downloaded file.
        :rtype: dict
        """
        result = self._run_command(
            ["plowdown", source["url"], "-o",
                output_directory, "--temp-rename"],
            stderr=open("/dev/null", "w")
        )

        result['host_name'] = source['host_name']

        if 'error' in result:
            return result

        temporary_filename = self.parse_output(
            result['host_name'], result['output'])
        result['filename'] = os.path.join(output_directory, filename)
        result.pop('output')

        os.rename(temporary_filename, result['filename'])

        return result

    def multiupload(self, filename, hosts):
        """Upload file to multiple hosts simultaneously

        The upload will be attempted for each host until the optimal file
        redundancy is achieved (a percentage of successful uploads) or the host
        list is depleted.

        :param filename: The filename of the file to upload.
        :type filename: str
        :param hosts: A list of hosts as defined in the master host list.
        :type hosts: list
        :returns:  A list of dicts with 'host_name' and 'url' keys for all
                   successful uploads or an empty list if all uploads failed.
        :rtype: list
        """
        manager = Manager()
        successful_uploads = manager.list([])

        def f(host):
            if len(successful_uploads) / float(len(hosts)) < \
                    settings.MIN_FILE_REDUNDANCY:
                # Optimal redundancy not achieved, keep going
                result = self.upload_to_host(filename, host)
                if 'error' in result:
                    self._host_errors[host] += 1
                else:
                    successful_uploads.append(result)

        multiprocessing.dummy.Pool(len(hosts)).map(
            f, self._hosts_by_success(hosts))

        return list(successful_uploads)

    def upload_to_host(self, filename, hostname):
        """Upload a file to the given host.

        This method relies on 'plowup' being installed on the system.
        If it succeeds, this method returns a dictionary with the host name,
        and the final URL. Otherwise, it returns a dictionary with the
        host name and an error flag.

        :param filename: The filename of the file to upload.
        :type filename: str
        :param hostname: The host you are uploading the file to.
        :type hostname: str
        :returns: Dictionary containing information about upload to host.
        :rtype: dict
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

        :param hostname: Name of host you are working with.
        :type hostname: str
        :param output: Dictionary containing information about a plowshare
                       action.
        :type output: dict
        :returns: Parsed and decoded output list.
        :rtype: list
        """
        if isinstance(output, bytes):
            output = output.decode('utf-8')
        return output.split()[-1]
