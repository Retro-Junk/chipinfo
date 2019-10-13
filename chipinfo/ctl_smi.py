# Silicon Motion (SMI) controller plugin

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

import controller
import scsi

_verbose = False

# Plugin name. Must be unique for a plugin
def Name():
	return "SMI"

# Return true if this plugin should be ever used
def Enabled():
	return True

# Register extra parameters to command line parser if needed
def AddParameters(parser):
	return

# Basic detection routine
# Should perform minimal amount of device interaction to ensure the device
# can be handled by this plugin and not set to unstable state in process
#
# Initial Inquiry data provided
# Return None if the controller can not be handled by this plugin

def Detect(dctl, inquiry, force=False, verbose=False):
	global _verbose
	_verbose = verbose

	# old models
	if len(inquiry) > 7:
		if  inquiry[5] == ord('s') \
		and inquiry[6] == ord('m') \
		and inquiry[7] == ord('i'):
			return SMI()

	# SMI3280+ models
	if len(inquiry) > 0x37:
		if  inquiry[0x35] == ord('s') \
		and inquiry[0x36] == ord('m') \
		and inquiry[0x37] == ord('i'):
			return SMI()

	if _verbose:
		print("%s: No smi tag found in inquiry data"%Name())

	if force:
		return SMI()

	return None

# All controller-related work resides in this class

class SMI():
	def __init__(self):
		#super().__init__(self)
		self.vendor = "SMI"
		self.model = "Unknown"
		return

	# Deep detection. Fill class fields with device-specific info
	def Detect(self, dctl, force=False):

		cdb = [0] * 16
		cdb[0] = 0xF0
		cdb[1] = 0x2A
		cdb[11] = 1		# sectors
		data = [0] * 512
		info = scsi.ScsiRequest(dctl, cdb, data)
		if info == None:
			return False

		#open("_smi_F02A.bin", "wb+").write(bytearray(info))

		if info[0x1AE] == ord('S') and info[0x1AF] == ord('M'):
			self.model = "".join([chr(x) for x in info[0x1AE:0x1AE + 8]]).split('\0')[0]
			self.version = "".join([chr(x) for x in info[0x190:0x1AE]]).split('\0')[0]
		else:
			return False

		return True

	def ControllerModel(self):
		return self.model

	def ControllerName(self):
		return self.vendor + " " + self.ControllerModel()

	# Gather device info and fill the report
	def ProcessDevice(self, dctl, report):

		report.append(("Controller", self.ControllerName()))
		report.append(("Firmware", self.version))

		flashinfo = self._GetFlashId(dctl)
		if flashinfo != None:
			flashids = [flashinfo[0x30+i*16:0x30+i*16 + 16] for i in range(8)]
			# pick a non-zero entry
			for flash in flashids:
				if flash[:8] != [0, 0, 0, 0, 0, 0, 0, 0]:
					break
			else:
				flash = flashids[0]
			report.append(("Flash ID", flash, "fid"))
		else:
			report.append(("Flash ID", "Unavailable"))

		return report

	def _GetFlashId(self, dctl):
		cdb = [0] * 16
		cdb[0] = 0xF0
		cdb[1] = 0x06
		cdb[11] = 1		# sectors
		data = [0] * 512
		info = scsi.ScsiRequest(dctl, cdb, data)
		return info
