plowshare-wrapper
=================

Python script for managing multi-host uploads using plowshare. After uploading it returns a JSON object with links and information about the uploads. 

#### Command Arguments

    plowshare-wrapper.py <file location> <number of hosts to upload to>

After uploading it should return some JSON data like this:

    {
      version: "0.1",
      datetime: "1391212800",
      file_hash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b", 
      "uploads": [
      { "host_name":"mediafire" , "url":"http://www.mediafire.com/?qorncpzfe74s9" }, 
      { "host_name":"rapidshare" , "url":"http://rapidshare.com/files/130403982" }
      ]
    }
