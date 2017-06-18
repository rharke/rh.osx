# Copyright (c) 2017 Ranger Harke
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import ctypes

from . import corefoundation

_da = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/DiskArbitration.framework/DiskArbitration')

# types
DADisk, DADiskRef = corefoundation.declare_cf_type('DADisk', corefoundation.CFType)
DASession, DASessionRef = corefoundation.declare_cf_type('DASession', corefoundation.CFType)

# constants
kDADiskDescriptionVolumeNameKey = corefoundation.CFStringRef.in_dll(
    _da, 'kDADiskDescriptionVolumeNameKey')
kDADiskDescriptionVolumePathKey = corefoundation.CFStringRef.in_dll(
    _da, 'kDADiskDescriptionVolumePathKey')

# functions
DADiskCopyDescription = _da.DADiskCopyDescription
DADiskCopyDescription.argtypes = [ DADiskRef ]
DADiskCopyDescription.restype = corefoundation.CFDictionaryRef

DADiskCreateFromBSDName = _da.DADiskCreateFromBSDName
DADiskCreateFromBSDName.argtypes = [ corefoundation.CFAllocatorRef, DASessionRef, ctypes.c_char_p ]
DADiskCreateFromBSDName.restype = DADiskRef

DASessionCreate = _da.DASessionCreate
DASessionCreate.argtypes = [ corefoundation.CFAllocatorRef ]
DASessionCreate.restype = DASessionRef
