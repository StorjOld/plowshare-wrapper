plowshare-wrapper
=================

Python wrapper for managing multi-host uploads using
[plowshare](https://code.google.com/p/plowshare/). After uploading it returns a
JSON object with links and information about file it uploaded. This wrapper
contains both a python module and a command line tool.

#### Installation

This module presumes that you already have plowshare installed on your system,
and that the plowup executable is available on your PATH. You can download
Debian, Ubuntu and other systems' packages from the official website.

You can clone this repository and use its modules directly. Alternatively, you
can build a package and install it through pip:

    python setup.py sdist
    sudo pip install dist/plowshare-0.1.0.tar.gz

#### Module usage

This module is composed of a single class, which can be used to upload a file
to multiple hosts at once. Example:

    import plowshare

    p = plowshare.Plowshare()
    p.upload("/home/jessie/documents/README.md", 5)


The above example uploads the given file to three different hosts, chosen at
random from a predefined list. You can also specify a list of hosts (plowshare
module names) to use:

    import plowshare

    p = plowshare.Plowshare(['turbobit', 'multiupload'])
    p.upload("/home/jessie/documents/README.md", 5)


The upload method returns a dictionary with information about the uploaded
file, and the hosts/URLs to which it uploaded the file. If some of the uploads
fail, it doesn't return an URL, but an error flag instead. It contains:

- version (if the json format changes, this will change too)
- file size (bytes)
- file hash (SHA-256)
- datetime (Unix timestamp)
- uploads (list of hosts and URLs)

Here's an example:

    {
      version: "0.1",
      datetime: "1391212800",
      filesize: "23124",
      file_hash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b",
      "uploads": [
        { "host_name": "mediafire",  "url":"http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":"http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error":true }
      ]
    }

#### Command line tool usage

plowshare-wrapper comes with a command line tool to upload a single file to a
given number of anonymous hosts. If you have installed it by just cloning this
repository, you can run:

    plowshare/tool.py <file location> <number of hosts to upload to>

If you installed it using pip, type:

    python -mplowshare.tool <file location> <number of hosts to upload to>


For example, the following uploads this project's README to five different
hosts, chosen at random:

    plowshare/tool.py README.md 5

The command prints out a json representation of the result status object.
Details on the format of the json can be seen above.
