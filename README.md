plowshare-wrapper
=================

Python script for managing multi-host uploads using plowshare. After uploading it returns a JSON object with links and information about the uploads. 

#### JSON Payload Example
{
  version: "0.1",
  datetime: "1391212800",
  file_hash: "6e163442e29ec8d7538bc86fe2c4a48778e8ae2254632f0889da753b1c357b1b", 
  "uploads": [
  { "firstName":"John" , "lastName":"Doe" }, 
  { "firstName":"Anna" , "lastName":"Smith" }, 
  { "firstName":"Peter" , "lastName":"Jones" }
  ]
}
