"""
# The MIT License (MIT)
#
# Copyright (c) 2019 VL
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
"""

import ioctl_win

# Platform-agnostic proxy methods

ScsiRequest = ioctl_win.ScsiRequest
GetCapacity = ioctl_win.GetCapacity
Device = ioctl_win.DeviceIoControl

# CDB helper class
class CDB:
	def __init__(self, size=16, cdb=[]):
		self.cdb = [0] * size
		for i in range(min(len(cdb), size)):
			self.cdb[i] = cdb[i]

	def Put(self, offset, value, size=0, little=True):
		if size == 0:
			v = value
			while v != 0:
				v >>= 8
				size += 1
		for i in range(size):
			if little:
				self.cdb[offset + i] = value & 255
			else:
				self.cdb[offset + size - i - 1] = value & 255
			value >>= 8
		return self

	# byte
	def PB(self, offset, value):
		self.cdb[offset] = value & 255
		return self

	# word, little-endian
	def PWL(self, offset, value):
		return self.Put(offset, value, 2, True)

	# word, big-endian
	def PWB(self, offset, value):
		return self.Put(offset, value, 2, False)

	# triplet, little-endian
	def PTL(self, offset, value):
		return self.Put(offset, value, 3, True)

	# triplet, big-endian
	def PTB(self, offset, value):
		return self.Put(offset, value, 3, False)

	# dword, little-endian
	def PDL(self, offset, value):
		return self.Put(offset, value, 4, True)

	# dword, big-endian
	def PDB(self, offset, value):
		return self.Put(offset, value, 4, False)

	@property
	def data(self):
		#return bytes(self.cdb)
		return self.cdb

# Standard SCSI operations

def Inquiry(dctl, page=0, size=0x38):
	cdb = [0] * 12
	cdb[0] = 0x12
	cdb[4] = size & 0xFF
	data = [0] * (size)
	return ScsiRequest(dctl, cdb, data)


def ReadSectors(dctl, lba, count):
	cdb = [0] * 12
	cdb[0] = 0x28
	cdb[2] = (lba >> 24) & 0xFF
	cdb[3] = (lba >> 16) & 0xFF
	cdb[4] = (lba >> 8) & 0xFF
	cdb[5] = lba & 0xFF
	cdb[7] = (count >> 8) & 0xFF
	cdb[8] = count & 0xFF
	data = [0] * (count * 512)
	return ScsiRequest(dctl, cdb, data)

def WriteSectors(dctl, lba, data):
	count = len(data) / 512
	cdb = [0] * 12
	cdb[0] = 0x2A
	cdb[2] = (lba >> 24) & 0xFF
	cdb[3] = (lba >> 16) & 0xFF
	cdb[4] = (lba >> 8) & 0xFF
	cdb[5] = lba & 0xFF
	cdb[7] = (count >> 8) & 0xFF
	cdb[8] = count & 0xFF
	return ScsiRequest(dctl, cdb, data, dataIn=False)
