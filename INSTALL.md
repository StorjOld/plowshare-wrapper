Installation
============

#### Dependencies

This module presumes that you already have plowshare installed in your system,
and that the plowup executable is available on your PATH. You can download
packages for Debian, Ubuntu and other systems from the official website.

If you're running Debian, you can install it using the following commands:

    wget https://plowshare.googlecode.com/files/plowshare4_1~git20140112.7ad41c8-1_all.deb
    sudo dpkg -i plowshare4_1~git20140112.7ad41c8-1_all.deb
    sudo apt-get -f install -y


#### Using pip

Install plowshare-wrapper using pip, directly from github:

    sudo pip install git+https://github.com/Storj/plowshare-wrapper

If you wish to install a specific version/tag, you can do it using the `@` syntax:

    sudo pip install git+https://github.com/Storj/plowshare-wrapper@v0.3.0
