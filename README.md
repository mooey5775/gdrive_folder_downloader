Google Drive Folder Downloader
==============================

A tool to download folders from Google Drive, battle tested with terabytes of data. Supports recursion through directories and continuing through partially completed downloads.

Uses PyDrive to handle Google Drive communication.

Files
-----

`downloader.py`: main downloader script
`requirements.txt`: Python requirements

Usage
-----

Before running the downloader, follow the instructions on the [PyDrive website](https://pythonhosted.org/PyDrive/quickstart.html#authentication) to set up OAuth authentication.

Run `python3 downloader.py -h` for help on command-line arguments.

Improvements
------------

- [ ] Use md5 hashes for integrity checking
- [ ] Fork PyDrive to prevent high memory usage
