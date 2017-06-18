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

from . import basetypes

# Python 2/3 compatibility
try:
    _basestring = basestring
except NameError:
    _basestring = str

_cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

def declare_cf_type(type_name, base_type):
    class CFType(base_type):
        pass
    CFType.__name__ = type_name
    CFTypeRef = ctypes.POINTER(CFType)

    # NB: Subclassing ctypes pointer types causes it to catch fire.
    #     Instead, we will just patch in the functionality we want.

    def _CFTypeRef_autorelease(self):
        """Declare that this CFTypeRef should be automatically released

        Observe the rules of CoreFoundation when using this function.
        Only call autorelease() when the "Create Rule" is applicable.
        If the "Get Rule" is applicable, then you MUST NOT call
        autorelease(), unless you have explicitly retained the object
        first.

        NB: If you pass a CFTypeRef byref (i.e. as an output parameter)
            and it gets mutated, the old value will not be released!
        """

        self._autorelease = True
        return self
    CFTypeRef.autorelease = _CFTypeRef_autorelease

    def _CFTypeRef___del__(self):
        if self and getattr(self, '_autorelease', False):
            CFRelease(self)
    CFTypeRef.__del__ = _CFTypeRef___del__

    return CFType, CFTypeRef

# types
CFType, CFTypeRef = declare_cf_type('CFType', ctypes.Structure)
CFAllocator, CFAllocatorRef = declare_cf_type('CFAllocator', CFType)
CFDictionary, CFDictionaryRef = declare_cf_type('CFDictionary', CFType)
CFMutableDictionary, CFMutableDictionaryRef = declare_cf_type('CFMutableDictionary', CFDictionary)
CFString, CFStringRef = declare_cf_type('CFString', CFType)
CFURL, CFURLRef = declare_cf_type('CFURL', CFType)

# Swizzle CFStringRef.from_param so that a string or bytes object can
# be passed to a function that expects a CFStringRef. Since the
# resultant object is ephemeral, autorelease() is automatically called
# so that it does not leak.
_CFStringRef_original_from_param = CFStringRef.from_param
def _CFStringRef_from_param(param):
    if isinstance(param, (_basestring, bytes)):
        if isinstance(param, _basestring):
            param = param.encode('utf-8')
        return CFStringCreateWithBytes(
            kCFAllocatorDefault, param, len(param),
            kCFStringEncodingUTF8, False).autorelease()
    else:
        return _CFStringRef_original_from_param(param)
CFStringRef.from_param = staticmethod(_CFStringRef_from_param)

def _CFStringRef___str__(self):
    if self:
        unicode_length = CFStringGetLength(self)
        byte_length = CFStringGetMaximumSizeForEncoding(unicode_length, kCFStringEncodingUTF8)
        buf = ctypes.create_string_buffer(byte_length + 1)
        CFStringGetCString(self, buf, byte_length + 1, kCFStringEncodingUTF8)
        return buf.value.decode('utf-8')
    else:
        raise ValueError('CFStringRef is null')
CFStringRef.__str__ = _CFStringRef___str__

CFIndex = ctypes.c_long
CFStringEncoding = ctypes.c_uint32
CFURLPathStyle = CFIndex

# constants
kCFAllocatorDefault = CFAllocatorRef.in_dll(_cf, 'kCFAllocatorDefault')

kCFStringEncodingUTF8 = 0x08000100
kCFURLPOSIXPathStyle = 0

# functions
CFDictionaryGetValue = _cf.CFDictionaryGetValue
CFDictionaryGetValue.argtypes = [ CFDictionaryRef, ctypes.c_void_p ]
CFDictionaryGetValue.restype = ctypes.c_void_p

CFRelease = _cf.CFRelease
CFRelease.argtypes = [ CFTypeRef ]
CFRelease.restype = None

CFRetain = _cf.CFRetain
CFRetain.argtypes = [ CFTypeRef ]
CFRetain.restype = CFTypeRef

CFStringCreateCopy = _cf.CFStringCreateCopy
CFStringCreateCopy.argtypes = [ CFAllocatorRef, CFStringRef ]
CFStringCreateCopy.restype = CFStringRef

CFStringCreateWithBytes = _cf.CFStringCreateWithBytes
CFStringCreateWithBytes.argtypes = [
    CFAllocatorRef, ctypes.c_char_p, CFIndex, CFStringEncoding, basetypes.Boolean ]
CFStringCreateWithBytes.restype = CFStringRef

CFStringGetCString = _cf.CFStringGetCString
CFStringGetCString.argtypes = [ CFStringRef, ctypes.c_char_p, CFIndex, CFStringEncoding ]
CFStringGetCString.restype = basetypes.Boolean

CFStringGetLength = _cf.CFStringGetLength
CFStringGetLength.argtypes = [ CFStringRef ]
CFStringGetLength.restype = CFIndex

CFStringGetMaximumSizeForEncoding = _cf.CFStringGetMaximumSizeForEncoding
CFStringGetMaximumSizeForEncoding.argtypes = [ CFIndex, CFStringEncoding ]
CFStringGetMaximumSizeForEncoding.restype = CFIndex

CFURLCopyFileSystemPath = _cf.CFURLCopyFileSystemPath
CFURLCopyFileSystemPath.argtypes = [ CFURLRef, CFURLPathStyle ]
CFURLCopyFileSystemPath.restype = CFStringRef
