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

vendors = {
	0x98: ("Toshiba", 8),
	0x45: ("Sandisk", 8),
	0x2C: ("Intel/Micron", 8),
	0xEC: ("Samsung", 6),
	0xAD: ("Hynix", 8),
	0xC2: ("Macronix", 6)
	}

def DecodeFlashId(fid):
	result = {}

	m = fid[0]
	if m in vendors:
		result["maker"] = vendors[m][0]
		result["fidlen"] = vendors[m][1]
	else:
		result["maker"] = "Unknown"
		result["fidlen"] = 8

	result["fid"] = fid[:result["fidlen"]]
	result["fidstr"] = " ".join("%02X"%x for x in result["fid"])

	#TODO: decode more fid values here

	return result

def GetFlashInfo(fid):
	info = DecodeFlashId(fid)
	result = "%s (%s)"%(info["fidstr"], info["maker"])
	return result
