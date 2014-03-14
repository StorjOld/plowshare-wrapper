Installation
============

#### Dependencies

This module presumes that you already have plowshare installed in your system,
and that the plowup executable is available on your PATH. You can download
packages for Debian, Ubuntu and other systems from the official website.

If you're running Debian, you can install it using the following commands:

    wget https://plowshare.googlecode.com/files/plowshare4_1~git20140112.7ad41c8-1_all.deb
    sudo dpkg -i plowshare4_1~git20140112.7ad41c8-1_all.deb
    sudo apt-get -f install


#### Using pip

To build and install with pip, you can clone the repository and do the
following commands:

    python setup.py sdist
    sudo pip install dist/plowshare-VERSION.tar.gz

To install it directly from github:

    sudo pip install git+https://github.com/Storj/plowshare-wrapper

