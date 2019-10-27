# Phison controller plugin

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
import argparse

_verbose = False

# Plugin name. Must be unique for a plugin
def Name():
	return "Phison"

# Return true if this plugin should be ever used
def Enabled():
	return True

# Register extra parameters to command line parser if needed
def AddParameters(parser):
	group = parser.add_argument_group(Name())
	group.add_argument("-x", "--extractfw", help="Extract firmware", action="store_true")
	return

# Basic detection routine
# Should perform minimal amount of device interaction to ensure the device
# can be handled by this plugin and not set to unstable state in process
#
# Initial Inquiry data provided
# If force set to True, use this controller even if detection fails
# Return None if the controller can not be handled by this plugin

def Detect(dctl, inquiry, force=False, verbose=False):
	global _verbose
	_verbose = verbose

	if len(inquiry) > 0x27:
		if  inquiry[0x24] == ord('P') \
		and inquiry[0x25] == ord('M') \
		and inquiry[0x26] == ord('A') \
		and inquiry[0x27] == ord('P'):
			return Phison()

	if _verbose:
		print("%s: No PMAP tag found in inquiry data"%Name())

	if force:
		return Phison()

	return None

# All controller-related work resides in this class

class Phison():
	def __init__(self):
		#super().__init__(self)
		self.vendor = "Phison"
		self.model = "Unknown"
		return

	# Deep detection. Fill class fields with device-specific info
	def Detect(self, dctl, force=False):

		info = self._GetInfoPage(dctl)

		if info == None:
			return False

		self.chip = info[0x1C6];
		self.model = "PS%02X%02X (0x%02X)"%(info[0x17E], info[0x17F], self.chip)
		self.product = str(info[0x9C:0x9C + 16]).split("\0")[0]
		self.version = "%d.%02X.%02X"%(info[0x94], info[0x95], info[0x96])
		self.date = "%02d/%02d/%02d"%(info[0x97], info[0x98], info[0x99])
		self.usbver = "%X"%info[0xF5]

		return True

	def ControllerModel(self):
		return self.model

	def ControllerName(self):
		return self.vendor + " " + self.ControllerModel()

	# Gather device info and fill the report
	def ProcessDevice(self, dctl, report):

		report.append(("Controller", self.ControllerName()))
		report.append(("Firmware", self.version + " " + self.date))

		flashinfo = self._GetFlashId(dctl)
		if flashinfo != None:
			flashids = [flashinfo[i*16:i*16 + 16] for i in range(8)]
			# pick a non-zero entry
			for flash in flashids:
				if flash[:8] != [0, 0, 0, 0, 0, 0, 0, 0]:
					break
			else:
				flash = flashids[0]
			report.append(("Flash ID", flash, "fid"))
		else:
			report.append(("Flash ID", "Unavailable"))

		#self._GetInfoPage(dctl, kind = "INFO")

		return report

	def _GetInfoPage(self, dctl, kind = "", size = 512 + 16):
		cdb = [0] * 12
		cdb[0] = 6
		cdb[1] = 5
		if kind != "":
			for i in range(min(len(kind), 10)):
				cdb[2 + i] = ord(kind[i])
		data = [0] * (size)
		info = scsi.ScsiRequest(dctl, cdb, data)
		if info != None:
			#open("_ph_0605%s.bin"%kind, "wb+").write(bytearray(info))
			if _verbose == True:
				if len(info) == 512 + 16:
					if info[512] != ord('I') or info[513] != ord('F'):
						print("* Warning: Strange info page mark")
		return info

	def _GetFlashId(self, dctl):
		cdb = [0] * 12
		cdb[0] = 6
		cdb[1] = 0x56 # also 4, but unavailable on newer firmwares
		data = [0] * 512
		info = scsi.ScsiRequest(dctl, cdb, data)
		return info
