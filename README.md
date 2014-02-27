plowshare-wrapper
=================

Python wrapper for managing multi-host uploads and downloads using
[plowshare](https://code.google.com/p/plowshare/). After uploading it returns a
JSON object with links and information about file it uploaded. This wrapper
contains both a python module and a command line tool.

#### Installation

This module presumes that you already have plowshare installed in your system,
and that the plowup executable is available on your PATH. You can download
Debian, Ubuntu and other systems' packages from the official website.

You can clone this repository and use its modules directly. Alternatively, you
can build a package and install it through pip:

    python setup.py sdist
    sudo pip install dist/plowshare-0.1.0.tar.gz

#### Module usage - Upload

This module is composed of a single class, which can be used to upload a file
to multiple hosts at once. Example:

    import plowshare

    p = plowshare.Plowshare()
    p.upload("/home/jessie/documents/README.md", 3)


The above example uploads the given file to three different hosts, chosen at
random from a predefined list. This list is a subset of the available plowshare
modules, limited to the ones that allow anonymous access. You can check it in
plowshare/hosts.py

You can also specify a list of hosts (plowshare module names) to use:

    import plowshare

    p = plowshare.Plowshare(['turbobit', 'multiupload', 'exoshare', 'rghost', 'bayfiles'])
    p.upload("/home/jessie/documents/README.md", 3)


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
      filehash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b",
      "uploads": [
        { "host_name": "mediafire",  "url":"http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":"http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error":true }
      ]
    }

#### Module usage - Download

You can also download uploaded files, by providing the json that the upload
method generated, and the directory where to download the file. This method
returns an object that contains the path where the file was downloaded, or
an object with the error message. Example:

    import plowshare

    info = {
      version: "0.1",
      datetime: "1391212800",
      filesize: "23124",
      filehash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b",
      "uploads": [
        { "host_name": "mediafire",  "url":"http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":"http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error":true }
      ]
    }

    p = plowshare.Plowshare()
    p.download(info, "/tmp/")

There are multiple errors that can occur. Here's a list of the currently supported errors:

    { "error": "unsupported format" }   # API version isn't supported
    { "error": "no valid uploads" }     # the provided json does not contain any valid upload
    { "error": "plowshare error" }      # plowshare blew up
    { "error": "file sizes mismatch" }  # downloaded file size does not match the provided one
    { "error": "file hashes mismatch" } # downloaded file hash does not match the provided one


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
