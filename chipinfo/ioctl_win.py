# The MIT License (MIT)
#
# Copyright (c) 2014-2016 Santoso Wijaya <santoso.wijaya@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sub-license, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ctypes
import ctypes.wintypes as wintypes
from ctypes import windll


LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPOVERLAPPED = wintypes.LPVOID
LPSECURITY_ATTRIBUTES = wintypes.LPVOID

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
GENERIC_EXECUTE = 0x20000000
GENERIC_ALL = 0x10000000

FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_RANDOM_ACCESS = 0x10000000

INVALID_HANDLE_VALUE = -1

NULL = 0
FALSE = wintypes.BOOL(0)
TRUE = wintypes.BOOL(1)


def _CreateFile(filename, access, mode, creation, flags):
    """See: CreateFile function

    http://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx

    """
    CreateFile_Fn = windll.kernel32.CreateFileW
    CreateFile_Fn.argtypes = [
            wintypes.LPWSTR,                    # _In_          LPCTSTR lpFileName
            wintypes.DWORD,                     # _In_          DWORD dwDesiredAccess
            wintypes.DWORD,                     # _In_          DWORD dwShareMode
            LPSECURITY_ATTRIBUTES,              # _In_opt_      LPSECURITY_ATTRIBUTES lpSecurityAttributes
            wintypes.DWORD,                     # _In_          DWORD dwCreationDisposition
            wintypes.DWORD,                     # _In_          DWORD dwFlagsAndAttributes
            wintypes.HANDLE]                    # _In_opt_      HANDLE hTemplateFile
    CreateFile_Fn.restype = wintypes.HANDLE

    return wintypes.HANDLE(CreateFile_Fn(filename,
                         access,
                         mode,
                         NULL,
                         creation,
                         flags,
                         NULL))


def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
    """See: DeviceIoControl function

    http://msdn.microsoft.com/en-us/library/aa363216(v=vs.85).aspx

    """
    DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
    DeviceIoControl_Fn.argtypes = [
            wintypes.HANDLE,                    # _In_          HANDLE hDevice
            wintypes.DWORD,                     # _In_          DWORD dwIoControlCode
            wintypes.LPVOID,                    # _In_opt_      LPVOID lpInBuffer
            wintypes.DWORD,                     # _In_          DWORD nInBufferSize
            wintypes.LPVOID,                    # _Out_opt_     LPVOID lpOutBuffer
            wintypes.DWORD,                     # _In_          DWORD nOutBufferSize
            LPDWORD,                            # _Out_opt_     LPDWORD lpBytesReturned
            LPOVERLAPPED]                       # _Inout_opt_   LPOVERLAPPED lpOverlapped
    DeviceIoControl_Fn.restype = wintypes.BOOL

    # allocate a DWORD, and take its reference
    dwBytesReturned = wintypes.DWORD(0)
    lpBytesReturned = ctypes.byref(dwBytesReturned)

    status = DeviceIoControl_Fn(devhandle,
                  ioctl,
                  inbuf,
                  inbufsiz,
                  outbuf,
                  outbufsiz,
                  lpBytesReturned,
                  None)

    return status, dwBytesReturned
    

class DeviceIoControl(object):

    def __init__(self, path):
        self.path = path
        self._fhandle = None

    def _validate_handle(self):
        if self._fhandle is None:
            raise Exception('No file handle')
        if self._fhandle.value == wintypes.HANDLE(INVALID_HANDLE_VALUE).value:
            raise Exception('Failed to open %s. GetLastError(): %d' %
                    (self.path, windll.kernel32.GetLastError()))

    def ioctl(self, ctl, inbuf, inbufsiz, outbuf, outbufsiz):
        self._validate_handle()
        return _DeviceIoControl(self._fhandle, ctl, inbuf, inbufsiz, outbuf, outbufsiz)

    def __enter__(self):
        self._fhandle = _CreateFile(
                self.path,
                GENERIC_READ | GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                OPEN_EXISTING,
                0)
                #FILE_ATTRIBUTE_NORMAL | FILE_FLAG_NO_BUFFERING | FILE_FLAG_RANDOM_ACCESS)
        self._validate_handle()
        return self

    def __exit__(self, typ, val, tb):
        try:
            self._validate_handle()
        except Exception:
            pass
        else:
            windll.kernel32.CloseHandle(self._fhandle)

def GetCapacity(dctl):
	# first, define the Structure in ctypes language
	class DISK_GEOMETRY(ctypes.Structure):
		"""See: http://msdn.microsoft.com/en-us/library/aa363972(v=vs.85).aspx"""
		_fields_ = [
			('Cylinders', wintypes.LARGE_INTEGER),
			('MediaType', wintypes.BYTE),   # MEDIA_TYPE
			('TracksPerCylinder', wintypes.DWORD),
			('SectorsPerTrack', wintypes.DWORD),
			('BytesPerSector', wintypes.DWORD)
			]

	IOCTL_DISK_GET_DRIVE_GEOMETRY = 0x70000

	disk_geometry = DISK_GEOMETRY()
	p_disk_geometry = ctypes.pointer(disk_geometry)

	status, _ = dctl.ioctl(IOCTL_DISK_GET_DRIVE_GEOMETRY,
			None, 0,                          # no input buffer
			p_disk_geometry, ctypes.sizeof(DISK_GEOMETRY))                                      

	if status:
		capacity = disk_geometry.BytesPerSector * disk_geometry.SectorsPerTrack * disk_geometry.TracksPerCylinder * disk_geometry.Cylinders
		return capacity
	else:
		raise Exception('IOCTL returned failure. GetLastError(): %d' % (windll.kernel32.GetLastError()))

	return None

class PointerSizeTest(ctypes.Structure):
		_fields_ = [
			('P', ctypes.POINTER(wintypes.BYTE))
			]

def ScsiRequest(dctl, cdb, data, dataIn=True):
	SenseLength = 24
	class SCSI_SENSE_DATA(ctypes.Structure):
		_fields_ = [
			('Data', wintypes.BYTE * SenseLength)
		]

	class SCSI_PASS_THROUGH_DIRECT(ctypes.Structure):
		_fields_ = [
			('Length', wintypes.USHORT),
			('ScsiStatus', wintypes.BYTE),
			('PathId', wintypes.BYTE),
			('TargetId', wintypes.BYTE),
			('Lun', wintypes.BYTE),
			('CdbLength', wintypes.BYTE),
			('SenseInfoLength', wintypes.BYTE),
			('DataIn', wintypes.BYTE),
			('Padding9', wintypes.BYTE * 3),
			('DataTransferLength', wintypes.DWORD),
			('TimeOutValue', wintypes.DWORD),
			('DataBuffer', ctypes.POINTER(wintypes.BYTE)),
			('SenseInfoOffset', wintypes.DWORD),
			('Cdb', wintypes.BYTE * 16)
			]

	class SCSI_PASS_THROUGH_DIRECT_WITH_SENSE(SCSI_PASS_THROUGH_DIRECT):
		_fields_ = [
			('Sense', wintypes.BYTE * SenseLength)
			]

	#print("0x%X"%(ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT)))
	#print("0x%X"%(ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_SENSE)))
	#print("0x%X"%(SCSI_PASS_THROUGH_DIRECT_WITH_SENSE.Sense.offset))

	IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x4D014

	buf = (wintypes.BYTE * len(data))()
	if dataIn == False:
		for i in range(len(data)):
			buf[i] = data[i] & 0xFF

	pass_through = SCSI_PASS_THROUGH_DIRECT_WITH_SENSE()
	pass_through.Length = ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT)
	pass_through.CdbLength = 16
	pass_through.SenseInfoLength = SenseLength
	pass_through.DataIn = 1 if dataIn == True else 0
	pass_through.DataBuffer = buf
	pass_through.DataTransferLength = len(buf)
	pass_through.TimeOutValue = 5
	pass_through.SenseInfoOffset = SCSI_PASS_THROUGH_DIRECT_WITH_SENSE.Sense.offset #0x30 #pass_through.Sense.offset

	# validate structure size
	if (ctypes.sizeof(PointerSizeTest) == 4 and pass_through.Length == 0x2C) \
	or (ctypes.sizeof(PointerSizeTest) == 8 and pass_through.Length == 0x38):
			pass
	else:
			raise Exception("Invalid SPTD structure size 0x%X, 0x%X"%(pass_through.Length, ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_SENSE)))

	for i in range(len(cdb)):
		if i >= 16:
			break
		pass_through.Cdb[i] = cdb[i] & 0xFF

	#TODO: fix CdbLength according to SCSI specs

	p_pass_through = ctypes.pointer(pass_through)

	status, _ = dctl.ioctl(IOCTL_SCSI_PASS_THROUGH_DIRECT,
			p_pass_through, ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_SENSE),
			p_pass_through, ctypes.sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_SENSE))

	#print(status, pass_through.ScsiStatus, pass_through.Sense[0])

	if status and pass_through.ScsiStatus == 0:
		if dataIn == True:
			for i in range(len(data)):
				data[i] = buf[i] & 0xFF
			return data
		else:
			return True
	else:
		raise Exception('SCSI request failure. GetLastError(): %d, ScsiStatus: %d' % (windll.kernel32.GetLastError(), pass_through.ScsiStatus))
	
	return None
