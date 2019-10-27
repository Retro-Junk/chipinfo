# Alcor Micro controller plugin

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
import struct

_verbose = False

# Plugin name. Must be unique for a plugin
def Name():
	return "Alcor"

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
	if len(inquiry) > 0x24:
		if  inquiry[0x20] == ord('8') \
		and inquiry[0x21] == ord('.') \
		and inquiry[0x22] == ord('0') \
		and inquiry[0x23] in [ord('0'), ord('1'), ord('7')]:
			return Alcor()

	if _verbose:
		print("%s: No alcor tag found in inquiry data"%Name())

	if force:
		return Alcor()

	return None

# All controller-related work resides in this class

class ChipModel:
	def __init__(self, Chip, Rev=None, Otp=None, Gen=0, Name=("???")):
		self.Chip = Chip
		self.Rev = Rev
		self.Otp = Otp
		self.Gen = Gen
		self.Name = ("AU" + x for x in Name)

knownControllers = [
	# from old tools
	ChipModel(Chip=0x0C0E,                           Gen= 0, Name=('9386')),
	ChipModel(Chip=0xAC43,                           Gen= 0, Name=('9387')),
	ChipModel(Chip=0xAA06,                           Gen= 0, Name=('6386/89')),
	ChipModel(Chip=0xAB41,                           Gen= 0, Name=('6980')), # newer tool report this as 6981
	ChipModel(Chip=0xAB42,                           Gen= 0, Name=('6981')),
	ChipModel(Chip=0xAE41,                           Gen= 0, Name=('6982')),
	#Old future models?
	#ChipModel(Chip=0xBA00,                           Gen= 1, Name=('6983')),
	#ChipModel(Chip=0xBB00,                           Gen= 0, Name=('6984')),
	#ChipModel(Chip=0xBC00,                           Gen= 0, Name=('6986')),
	#ChipModel(Chip=0xDA00,                           Gen= 0, Name=('6986')),
	#ChipModel(Chip=0xEA00,                           Gen= 0, Name=('6987')),
	#ChipModel(Chip=0xBD00,                           Gen= 0, Name=('6986')),
	#ChipModel(Chip=0xCA00,                           Gen= 0, Name=('6990')),
	#ChipModel(Chip=0xD000,                           Gen= 0, Name=('6986T')),
	# from new tools
	ChipModel(Chip=0xAC43,                           Gen= 0, Name=('9387')),
	ChipModel(Chip=0xAB41,                           Gen= 0, Name=('6981')),
	ChipModel(Chip=0xAB42,                           Gen= 0, Name=('6981')),
	ChipModel(Chip=0xAB43,                           Gen= 0, Name=('6981')),
	ChipModel(Chip=0xAE41,                           Gen= 0, Name=('6982')),
	ChipModel(Chip=0xAE42,                           Gen= 0, Name=('6982')),
	ChipModel(Chip=0xBA01,                           Gen= 1, Name=('6983')),
	ChipModel(Chip=0xBB06,                           Gen= 1, Name=('6984')),
	ChipModel(Chip=0xBB07,                           Gen= 1, Name=('6984')),
	ChipModel(Chip=0xBB09,                           Gen= 1, Name=('6984')),
	ChipModel(Chip=0xBC01,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBC07,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD01,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD02,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD03,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD04,                           Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD05, Rev=0x08,                 Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD06, Rev=0x08,                 Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xBD06, Rev=0x0C,                 Gen= 2, Name=('6983',       '6986')),
	ChipModel(Chip=0xCA01, Rev=0x00,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA02, Rev=0x00,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA03, Rev=0x00,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA03, Rev=0x10,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA03, Rev=0x20,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA03, Rev=0x40,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA03, Rev=0xC0,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA04, Rev=0xC0,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA05, Rev=0xC0,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA06, Rev=0x00,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA07, Rev=0x00,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA07, Rev=0x40,                 Gen= 5, Name=('6987',       '6990')),
	ChipModel(Chip=0xCA09, Rev=0x00,                 Gen= 5, Name=('6987AN',     '6991')),
	ChipModel(Chip=0xCA09, Rev=0x10,                 Gen= 5, Name=('6987AN',     '6991')),
	ChipModel(Chip=0xCA09, Rev=0x20,                 Gen= 5, Name=('6987AN',     '6991')),
	ChipModel(Chip=0xCA09, Rev=0x40,                 Gen= 5, Name=('6987AN',     '6991')),
	ChipModel(Chip=0xCA09, Rev=0xC0,                 Gen= 5, Name=('6987AN',     '6991')),
	ChipModel(Chip=0xD002, Rev=0x0F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD003, Rev=0x0F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD004, Rev=0x0F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD004, Rev=0x4F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD005, Rev=0x0F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD005, Rev=0x4F,                 Gen= 3, Name=('6985',       '6992')),
	ChipModel(Chip=0xD203, Rev=0x0F,                 Gen= 4, Name=('6985B',      '6996')),
	ChipModel(Chip=0xD203, Rev=0x4F,                 Gen= 4, Name=('6985B',      '6996')),
	ChipModel(Chip=0xD403, Rev=0x0F,                 Gen= 4, Name=('6985B',      '6996')),
	ChipModel(Chip=0xD403, Rev=0x4F,                 Gen= 4, Name=('6985B',      '6996')),
	ChipModel(Chip=0xCD03, Rev=0x80,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xCD03, Rev=0xC0,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xCB04, Rev=0x80,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCB04, Rev=0xC0,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCB05, Rev=0x80,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCB05, Rev=0xC0,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCB06, Rev=0x80,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCB06, Rev=0xC0,                 Gen= 6, Name=('6987T',      '6990T')),
	ChipModel(Chip=0xCC01, Rev=0x80,                 Gen= 7, Name=('6989NL',     '6998NL')),
	ChipModel(Chip=0xCC01, Rev=0xC0,                 Gen= 7, Name=('6989NL',     '6998NL')),
	ChipModel(Chip=0xCF02, Rev=0x80,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xCF02, Rev=0xC0,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xCF02, Rev=0x81,                 Gen= 8, Name=('6989NL',     '6998NL')),
	ChipModel(Chip=0xCF02, Rev=0xC1,                 Gen= 8, Name=('6989NL',     '6998NL')),
	ChipModel(Chip=0xCE01, Rev=0x80,                 Gen= 6, Name=('6989L',      '6998L')),
	ChipModel(Chip=0xCE01, Rev=0xC0,                 Gen= 6, Name=('6989L',      '6998L')),
	ChipModel(Chip=0xCE02, Rev=0x80,                 Gen= 6, Name=('6989L',      '6998L')),
	ChipModel(Chip=0xCE02, Rev=0xC0,                 Gen= 6, Name=('6989L',      '6998L')),
	ChipModel(Chip=0xE001, Rev=0x80,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE001, Rev=0xC0,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE203, Rev=0x80,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE203, Rev=0xC0,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE204, Rev=0x80,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE204, Rev=0xC0,                 Gen= 8, Name=('6989',       '6998')),
	ChipModel(Chip=0xE101, Rev=0x80,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE101, Rev=0xC0,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE102, Rev=0x80,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE102, Rev=0xC0,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE103, Rev=0x80,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE103, Rev=0xC0,                 Gen= 8, Name=('6989N',      '6998N')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0xFF13EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0xF013EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0x0F13EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0xFFFFFFFF, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0x0013EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0xF012CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0x1F12CA50, Gen= 8, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE302, Rev=0x80, Otp=0x1012CA50, Gen= 8, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x0F13EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0xFFFFFFFF, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x0013EA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0xF012CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x1F12CA50, Gen= 8, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x1012CA50, Gen= 8, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0xF052CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x2F12CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x2F92CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x2012CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x2092CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x3F12CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE304, Rev=0x80, Otp=0x3012CA50, Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE509, Rev=0x80,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE509, Rev=0xC0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE50B, Rev=0x80,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE50B, Rev=0xC0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE50B, Rev=0x88,                 Gen= 9, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE50B, Rev=0xC8,                 Gen= 9, Name=('6989ANL',    '6998ANL')),
	ChipModel(Chip=0xE50E, Rev=0x80,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE50E, Rev=0xC0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE50E, Rev=0xE0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE512, Rev=0x80,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE512, Rev=0xC0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE512, Rev=0xE0,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE602, Rev=0x80,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE602, Rev=0xC0,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE602, Rev=0xE0,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE603, Rev=0x80,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE603, Rev=0xC0,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE603, Rev=0xE0,                 Gen= 8, Name=('6989AN',     '6998AN')),
	ChipModel(Chip=0xE802, Rev=0x80, Otp=0xFF13EA50, Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xE802, Rev=0x80, Otp=0xF013EA50, Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xEB02, Rev=0x80,                 Gen= 9, Name=('6989SN',     '6998SN')),
	ChipModel(Chip=0xEC05, Rev=0x80,                 Gen=11, Name=('6989SN-GT',  '6998SN')),
	ChipModel(Chip=0xEC05, Rev=0xC0,                 Gen=11, Name=('6989SN-GT',  '6998SN')),
	ChipModel(Chip=0xEC05, Rev=0xE0,                 Gen=11, Name=('6989SN-GT',  '6998SN')),
	ChipModel(Chip=0xEC07, Rev=0x80,                 Gen=11, Name=('6989SN-GT',  '6998SN')),
	ChipModel(Chip=0xEC07, Rev=0xC0,                 Gen=11, Name=('6989SN-GT',  '6998SN')),
	ChipModel(Chip=0xEF00, Rev=0x80,                 Gen=12, Name=('6989SNL',    '6998SNL')),
	ChipModel(Chip=0xEF01, Rev=0x80,                 Gen=12, Name=('6989SNL',    '6998SNL')),
	ChipModel(Chip=0xEF01, Rev=0xCC,                 Gen=12, Name=('6989SNM',    '6998SNM')),
	ChipModel(Chip=0xEF01, Rev=0xC0,                 Gen=12, Name=('6989SN-GTA', '6998SN')),
	ChipModel(Chip=0xEF01, Rev=0xE0,                 Gen=12, Name=('6989SN-GTA', '6998SN')),
	ChipModel(Chip=0xEF01, Rev=0x8C,                 Gen=12, Name=('6989SN-GTA', '6998SN')),
	ChipModel(Chip=0xEF01, Rev=0x8E,                 Gen=12, Name=('6989SNM',    '6998SNM')),
	ChipModel(Chip=0xF101, Rev=0x00,                 Gen=13, Name=('6989SNL-B',  '6998SNL')),
	ChipModel(Chip=0xF101, Rev=0x80,                 Gen=13, Name=('6989SNL-B',  '6998SNL')),
	ChipModel(Chip=0xF101, Rev=0xC0,                 Gen=13, Name=('6989SNL-B',  '6998SNL')),
	ChipModel(Chip=0xF204, Rev=0x00,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF204, Rev=0x80,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF204, Rev=0xC0,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF206, Rev=0xC1,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF206, Rev=0x80,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF206, Rev=0xC0,                 Gen=14, Name=('6989SN-GTB', '6998SN')),
	ChipModel(Chip=0xF500, Rev=0x00,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF500, Rev=0x81,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF500, Rev=0x80,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF500, Rev=0xC0,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF500, Rev=0xC1,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF502, Rev=0x00,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF502, Rev=0x81,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF502, Rev=0x80,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF502, Rev=0xC0,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF502, Rev=0xC1,                 Gen=15, Name=('6989SN-GTC', '6998SN')),
	ChipModel(Chip=0xF700, Rev=0x00,                 Gen=15, Name=('6989SN-GTD', '6998SN')),
	ChipModel(Chip=0xF700, Rev=0x80,                 Gen=15, Name=('6989SN-GTD', '6998SN')),
	ChipModel(Chip=0xF700, Rev=0xC0,                 Gen=15, Name=('6989SN-GTD', '6998SN')),
	ChipModel(Chip=0xF700, Rev=0xC3,                 Gen=15, Name=('6989SN-GTD', '6998SN')),
	ChipModel(Chip=0xF800, Rev=0x00,                 Gen=15, Name=('6989SN-GTE', '6998SN')),
	ChipModel(Chip=0xF800, Rev=0x80,                 Gen=15, Name=('6989SN-GTE', '6998SN')),
	ChipModel(Chip=0xF800, Rev=0xC0,                 Gen=15, Name=('6989SN-GTE', '6998SN')),
	ChipModel(Chip=0xF900, Rev=0x80,                 Gen=15, Name=('6989SN-GTF', '6998SN')),
	ChipModel(Chip=0xFA00, Rev=0x80,                 Gen=15, Name=('6989SN-GTF', '6998SN')),
	ChipModel(Chip=0xF000, Rev=0x00,                 Gen=10),	# some test prototype?
	]

class Alcor():

	def __init__(self):
		#super().__init__(self)
		self.vendor = "Alcor Micro"
		self.model = "Unknown"
		self.chips = []
		self.chipver = None
		self.chiprev = None
		self.chipotp = None
		self.chipgen = -1
		self.badblocks = 0
		return

	# Deep detection. Fill class fields with device-specific info
	def Detect(self, dctl, force=False):

		cdb = [0] * 16
		cdb[0] = 0x9A
		data = [0] * 512
		info = scsi.ScsiRequest(dctl, cdb, data)
		if info == None:
			if _verbose:
				print("%s: Command 0x%02X failed"%(Name(), cdb[0]))
			return False

		if _verbose: open("_alc_9A.bin", "wb+").write(bytearray(info))

		self.chipver = info[4] * 256 + info[5]

		for chip in knownControllers:
			if chip.Chip == self.chipver:
				self.chips.append(chip)
				self.chipgen = chip.Gen

		if info[0x2B] == 0xAA:
			self.fwloaded = info[0x2C] != 0
			self.fwversionold = info[0x2D] * 256 + info[0x2E]
			# 0x2E is always zero?

		if self.chipver in [0x0C0E, 0xAA06]:
			self.badblocks = info[0x25]
		elif self.fwloaded:
			self.badblocks = info[0x25] * 4

		return True

	def ControllerModel(self):
		for chip in self.chips:
			if chip.Rev == None or chip.Rev == self.chiprev:
				self.model = " / ".join(chip.Name)
				break
		else:
			self.model = " / ".join(chip.Name) + " variant"

		self.chipverstr = "%04X"%self.chipver
		if self.chips[0].Rev != None and self.chiprev != None:
			self.chipverstr += "-%02X"%self.chiprev

		# TODO: ignore OTP for now

		return self.model + " [" + self.chipverstr + "]"

	def ControllerName(self):
		return self.vendor + " " + self.ControllerModel()

	# Gather device info and fill the report
	def ProcessDevice(self, dctl, report):
			
		cdb = [0] * 16
		cdb[0] = 0xFA
		cdb[1] = 0x0E
		data = [0] * 512
		info = scsi.ScsiRequest(dctl, cdb, data)
		if info == None:
			if _verbose:
				print("%s: Command 0x%02X%02X failed"%(Name(), cdb[0], cdb[1]))
		else:
			if _verbose: open("_alc_FA0E.bin", "wb+").write(bytearray(info))
			self.chiprev = info[0xB]

		report.append(("Controller", self.ControllerName()))

		if self.fwloaded:
			if self.chipgen == 0:
				self.fwversion = self.fwversionold
				self.fwversionstr = "%02d%02d"%(self.fwversionold >> 8, self.fwversionold & 255)
			else:
				self.fwversion = self._GetFirmwareVersion(dctl)
				if self.fwversion <= 0xFFFF:
					self.fwversionstr = "%04X"%self.fwversion
				else:
					self.fwversionstr = "%08X"%(self.fwversion & 0xFFFFFFFF)
				if(self.fwversion & 0xFF000000) == 0xF0000000:
					self.fwversionstr += "_%02X"(self.fwversion >> 32)
		else:
			self.fwversionstr = "Not loaded"

		report.append(("Firmware", self.fwversionstr))

		flashinfo = self._GetFlashId(dctl)
		if flashinfo != None:
			#TODO: 8-byte entries on old versions?
			flashids = [flashinfo[i*16:i*16 + 6] for i in range(8)]
			# pick a non-zero entry
			for flash in flashids:
				if flash[:6] != [0, 0, 0, 0, 0, 0]:
					break
			else:
				flash = flashids[0]
			report.append(("Flash ID", flash, "fid"))
		else:
			report.append(("Flash ID", "Unavailable"))

		return report


	def _GetFirmwareVersion(self, dctl):
		version = -1
		cdb = scsi.CDB(cdb=[0xFA, 0x0E])
		data = [0] * 512
		data = scsi.ScsiRequest(dctl, cdb.data, data)

		if data[6] >= 0xF0:
			version = (data[6] << 24) | (data[4] << 16) | (data[5] << 8) | data[7]
		elif data[6] == 0x36:
			version = (data[6] << 24) | (data[7] << 16) | (data[4] << 8) | data[5]
		else:
			version = (data[6] << 8) | data[7]

		data = [0] * 512 * 18
		cdb = scsi.CDB(cdb=[0xFA, 0x10])
		cdb.PB(2, len(data) / 512).PB(4, 0xC0)
		data = scsi.ScsiRequest(dctl, cdb.data, data, mayFail=True)

		if data != None:
			if _verbose: open("_alc_FA10.bin", "wb+").write(bytearray(data))
			if data[0xFFB] == 0x51:
				version |= data[0xFFA] << 32
		else:
			if _verbose:
				print("%s: Command 0x%02X%02X failed (norm for old chips)"%(Name(), cdb.data[0], cdb.data[1]))

		return version

	def _GetFlashId(self, dctl):
		if self.chipgen == 0:
			info = []
			for ch in [0, 1, 3, 7]:
				# TODO: send nand reset command first?
				# 4-byte fid, 2 per channel
				cdb = [0] * 16
				cdb[0] = 0xD0
				cdb[1] = ch
				cdb[2] = 0xF0
				cdb[3] = 0x90
				cdb[4] = 0xF1
				cdb[5] = 1
				cdb[6] = 0
				cdb[7] = 0xF2
				cdb[8] = 4
				data = [0] * 512
				data = scsi.ScsiRequest(dctl, cdb, data)
				if _verbose: open("_alc_D0%02X.bin"%ch, "wb+").write(bytearray(data))
				info += data[0:16]
				info += data[0x80:0x80+16]
			return info
		else:
			cdb = [0] * 16
			cdb[0] = 0xFA
			cdb[1] = 0
			data = [0] * 512
			info = scsi.ScsiRequest(dctl, cdb, data)
			if _verbose: open("_alc_FA00.bin", "wb+").write(bytearray(info))
			return info
