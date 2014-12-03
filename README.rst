Plowshare Wrapper
=================

|Build Status| |Coverage Status| |PyPI version|

Python wrapper for managing multi-host uploads and downloads using
`plowshare`_. After uploading it returns an object with links to the
file it uploaded. This wrapper contains both a Python module and a
command line tool.

Installation
------------

Check `INSTALL.md`_ for installation instructions.

Module Usage
------------

Upload
~~~~~~

This module is composed of a single class, which can be used to upload a
file to multiple hosts at once. Example:

::

    import plowshare

    p = plowshare.Plowshare()
    p.upload('/home/jessie/documents/README.md', 3)

The above example uploads the given file to three different hosts,
chosen at random from a predefined list. This list is a subset of the
available plowshare modules, limited to the ones that allow anonymous
access. You can check it in plowshare/hosts.py

You can also specify a list of hosts (plowshare module names) to use:

::

    import plowshare

    p = plowshare.Plowshare(['turbobit', 'multiupload', 'exoshare', 'rghost', 'bayfiles'])
    p.upload('/home/jessie/documents/README.md', 3)

The upload method returns an array of objects with the hosts and URLs to
which it uploaded the file. If some of the uploads fail, it doesn’t
return an URL, but an error flag instead.

Here’s an example:

::

    [
        { "host_name": "mediafire",  "url":   "http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":   "http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error": true }
    ]

Download
~~~~~~~~

You can also download uploaded files, by providing the object that the
upload method generated, and the directory and filename where to
download the file. This method returns an object that contains the path
where the file was downloaded, or an object with the error message.
Example:

::

    import plowshare

    uploads = [
        { 'host_name': 'mediafire',  'url':'http://www.mediafire.com/?qorncpzfe74s9' },
        { 'host_name': 'rapidshare', 'url':'http://rapidshare.com/files/130403982' },
        { 'host_name': 'anonfiles',  'error':true }
    ]

    p = plowshare.Plowshare()
    p.download(info, '/tmp/', 'readme_copy.md')

If multiple sources are provided, they are used as failovers for
downloading the file. If at least one source is successful, the others
won’t be attempted and ``download()`` will return an object with the
full path filename and the first host it successfuly downloaded it from:

::

    { "host_name": "mediafire", "filename": "/tmp/readme_copy.md" }

There are multiple errors that can occur. Here’s a list of the currently
supported errors:

::

    { "error": "no valid sources" }     # the provided object does not contain a valid source.

.. _plowshare: https://code.google.com/p/plowshare/
.. _INSTALL.md: INSTALL.md

.. |Build Status| image:: https://travis-ci.org/Storj/plowshare-wrapper.svg
   :target: https://travis-ci.org/Storj/plowshare-wrapper
.. |Coverage Status| image:: https://coveralls.io/repos/Storj/plowshare-wrapper/badge.png?branch=master
   :target: https://coveralls.io/r/Storj/plowshare-wrapper?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/plowshare.svg
   :target: http://badge.fury.io/py/plowshare