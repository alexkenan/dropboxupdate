# dropboxupdate

## A basic git push/pull between Mac and Raspberry Pi


### Summary
This script pushes a directory to Dropbox and allows another user to pull this directory onto their computer and overwrites the existing file.

Used to sync folders of Python code between Mac and Raspberry Pi but is now updated to sync between any two \*nix computers.

### Examples

`python3 dbxupdate.py "backup" "/Users/Alex/Documents/Python3/" "None" -push`

* `-push` means that we are pushing or uploading to Dropbox
* `backup` is the folder to be pushed/uploaded
* `/Users/Alex/Documents/Python3/` is the absolute path to `backup`'s parent folder
* `None` is the location to download the folder, but this isn't used in the `push` functionality so that is why it is `None`


`python3 dbxupdate.py "backup" "/home/pi/" "/media/pi/USB/Code/" -pull`
* `-pull` means that we are pulling or downloading from Dropbox
* `backup` is the folder to be pulled/downloaded
* `/home/pi/` is a temporary download location
* `/media/pi/USB/Code/` is the final download location
