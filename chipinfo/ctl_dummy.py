# Dummy controller plugin template

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

import scsi

_verbose = False

# Plugin name. Must be unique for a plugin
def Name():
	return "Dummy"

# Return true if this plugin should be ever used
def Enabled():
	return True

# Register extra parameters to command line parser if needed
def AddParameters(parser):
	return

# Basic detection routine
# Should perform minimal amount of device interaction to ensure the device
# can be handled by this plugin and not set to unstable state in process
def Detect(dctl, inquiry, force=False, verbose=False):
	global _verbose
	_verbose = verbose

	#return Dummy()
	return None		# never detect anything in this dummy example

# All controller-related work resides in this class
class Dummy:
	def __init__(self):
		self.vendor = "Acme corp."
		self.model = "Unknown"
		return

	# Deep detection. Fill class fields with device-specific info
	# Return false in case of mis-detection by basic detection method
	def Detect(self, dctl, force=False):
		self.model = "T1000"
		return True

	def ControllerModel(self):
		return self.model

	def ControllerName(self):
		return self.vendor + " " + self.ControllerModel()

	def ProcessDevice(self, dctl, report):
		report.append(("Controller", self.ControllerName()))
		return report
