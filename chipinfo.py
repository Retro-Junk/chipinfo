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

import sys
sys.dont_write_bytecode = True	# for debugging
import datetime
import argparse
sys.path.append("chipinfo")
import scsi
import controller
import flash

_version = "ChipInfo/CHIE v0.3 *ALPHA* by VL // 2019/10/27"

def ProcessDevice(deviceName, report=[], verbose=False, friendlyName=""):

	if friendlyName == "":
		friendlyName = deviceName

	try:
		report.append(("Device", friendlyName))
		with scsi.Device(deviceName) as dctl:

			capacity = scsi.GetCapacity(dctl)
			report.append(("Capacity", capacity, "size"))

			detected = False
			for ctl in controller.DetectController(dctl, verbose=verbose):
				ctl.ProcessDevice(dctl, report)
				detected = True
			if not detected:
				report.append(("Controller", "Unknown"))
		#report.append(("Status", "OK"))
	except Exception as e:
		#print(msg)
		report.append(("Error", e))
		#report.append(("Status", msg))

	return report

def ProcessDeviceByLetter(deviceLetter, report=[], verbose=False):
	letter = deviceLetter[0].upper()
	device = "\\\\.\\" + letter + ":"
	return ProcessDevice(device, report, verbose, friendlyName=letter + ":")

def FormatValue(value, format):
	if value == None:
		return "Unavailable"

	if format == "X":
		return "%X"%value
	if format == "size":
		return "%d byte(s)"%value
	if format == "fid":
		return flash.GetFlashInfo(value)

	return value

def PrintReport(report, filename=None):
	rawreport = []
	for entry in report:
		key = entry[0]
		# key = Translate(key)
		value = FormatValue(entry[1], entry[2]) if len(entry) > 2 else entry[1]
		rawreport.append((key, value))

	keywidth = 0
	for entry in rawreport:
		keywidth = max(keywidth, len(entry[0]))

	if filename != None:
		f = open(filename, "wt")
		f.write(_version + "\n")
	else:
		f = None

	for entry in rawreport:
		key = entry[0]
		value = entry[1]
		line = "{key:{kw}}: {value}".format(key=key, kw=keywidth, value=value)
		print(line)
		if f != None:
			f.write(line + "\n")

	if f != None:
		f.close()

def SetCommonParams(parser):
	parser.add_argument("device", help="Device name (in form of F: (volume F) or /dev/sdb)", type=str)
	#TODO: also support #0 (PhysicalDrive 0) or :VID:PID or &intance
	parser.add_argument("-b", "--benchmark", help="Perform IO benchmark", action="store_true")
	parser.add_argument("-r", "--report", help="Write report to file", dest="report")
	parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
	parser.add_argument("-p", "--plugin", help="Force plugin(s)", type=str)

def Main():
	print(_version)
	controller.LoadPlugins()
	print("Supported controllers: %s"%(",".join(controller.GetPlugins())))
	print("")

	#TODO: need to apply plugin's options now to show correct help

	parser = argparse.ArgumentParser()
	SetCommonParams(parser)
	args = parser.parse_known_args()[0]
	plugins = args.plugin.split(",") if args.plugin else None
	#controller.LoadPlugins(plugins, args.verbose)
	# all plugins are already loaded, just remove those we don't want
	if plugins != None:
		controller.UnloadPlugins(keep=plugins)
		print("Selected controllers: %s"%(",".join(controller.GetPlugins())))

	# register controller-specific options and parse args again
	for plugin in controller.plugins:
		controller.plugins[plugin].AddParameters(parser)
	args = parser.parse_args()

	report = ProcessDeviceByLetter(args.device, verbose=args.verbose)

	if args.benchmark:
		#TODO benchmark the device
		pass

	PrintReport(report, args.report)

Main()
