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
import os
import glob
import imp

plugins = {}

"""
	Load controller plugins
	If names specified, load named plugins only
"""
def LoadPlugins(names=None, verbose=False):
	root = os.path.dirname(os.path.abspath(__file__))
	for p in glob.glob(root + "/ctl_*.py"):
		pn = os.path.splitext(os.path.basename(p))[0]
		fp, path, desc = imp.find_module(pn)
		#print(fp, path, desc)
		try:
			plugin = imp.load_module(pn, fp, path, desc)
			if plugin.Enabled():
				if names == None or names == [] or plugin.Name() in names:
					plugins[plugin.Name()] = plugin
		finally:
			if fp: fp.close
		# TODO: IDEA: let plugin to dictate which other plugins it want to disable
		#pn = GetPlugins()
		#for p in pn:
		#	if p in plugins:
		#		for candidate in p.OverridePlugins():
		#			if candidate in plugins:
		#				del(plugins[candidate])
	# TODO: sort by names
	return

"""
	Unload specified plugins
	If keep is specified, do not unload these plugins
"""
def UnloadPlugins(names=None, keep=None):
	pns = GetPlugins()
	for name in pns:
		if keep != None and name in keep:
			continue
		if names == None or name in names:
			del(plugins[name]) 

def GetPlugins():
	return plugins.keys()

"""
	Controller detection
"""
def DetectController(dctl, verbose=False):
	inquiry = scsi.Inquiry(dctl)
	if verbose:
		open("_inq_12.bin", "wb+").write(bytearray(inquiry))

	for pn in plugins:
		plugin = plugins[pn]
		ctl = plugin.Detect(dctl, inquiry, verbose=verbose)
		if ctl != None:
			if ctl.Detect(dctl) == True:
				yield ctl

	#return None


"""
	Plugin interface class
"""
class BasePlugin:
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
