Chip Information Extractor
By VL, 2019

This program tries to extract information about internal hardware and software
components of various PC devices. Primarily USB/SATA/etc disk devices at this moment.
It works similar to ChipGenius and FlashDrive Information Extractor programs,
except for:
- It's free and open-source
- It doesn't contain any timebombs, "call home" functionality or other questionable stuff
- It's built with cross-platform portability and easy extensibility in mind.

Currently, Chip Information Extractor is in its early stages of development.
Things working so far:
- Windows IO via ctypes/SPTI
- Retrieve information from Phison and SMI-based flash drives.


Things to be done:
- Linux support via python-scsi
- Disk IO benchmark (diskspd on Windows)
- Add more controllers
- Simple GUI wrapper.


Usage:

chipinfo.py devicename

where devicename is a disk drive letter (Windows) or device path (/dev/... on linux).
Admin/su rights may be required for certain functions. Make sure device is not used
by other programs while testing it with CIEX.


Disclaimer:

This program uses vendor-specific and often undocumented device features discovered
by means of trial-and-error or reverse engineering. Under no circumstances author of
this program guarantees or liable for its safety for a device under test. You use it
at your own risk!


History:

2010/10/13 v0.2 - Command line parameters handling
2019/10/06 v0.1 - Basic prototype version, SMI and Phison support
