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

from . import basetypes, corefoundation

_iokit = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/IOKit.framework/IOKit')

# types
class io_object_t(basetypes.mach_port_t):
    def __del__(self):
        if self and getattr(self, '_autorelease', False):
            IOObjectRelease(self)

    def autorelease(self):
        """Declare that this io_object_t should be automatically released

        NB: If you pass an io_object_t byref (i.e. as an output
            parameter) and it gets mutated, the old value will not be
            released!
        """

        self._autorelease = True
        return self

# NB: io_object_t and its decendants are really just integers (not
#     not pointers), so if we made them classes, then ctypes wouldn't
#     be able to cast between them. We will forego type safety and just
#     make all the types equal, like it is in C anyways.
io_iterator_t = io_object_t
io_registry_entry_t = io_object_t

IOOptionBits = ctypes.c_uint32

# io_name_t is defined as `char[128]`, but it is common practice to
# pass a `const char*` of arbitrary length to functions that take a
# `const io_name_t`
const_io_name_t = ctypes.c_char_p
mutable_io_name_t = type(ctypes.create_string_buffer(128))

# constants
IO_OBJECT_NULL = 0x00000000

kIORegistryIterateRecursively = 0x00000001
kIORegistryIterateParents = 0x00000002

kIOBlockStorageDeviceClass = b'IOBlockStorageDevice'
kIOCDBlockStorageDeviceClass = b'IOCDBlockStorageDevice'
kIOServicePlane = b'IOService'
kIOMediaClass = b'IOMedia'
kIOCDMediaClass = b'IOCDMedia'
kIODVDMediaClass = b'IODVDMedia'
kIOBSDNameKey = b'BSD Name'

# functions
IOIteratorNext = _iokit.IOIteratorNext
IOIteratorNext.argtypes = [ io_iterator_t ]
IOIteratorNext.restype = io_object_t

IOMasterPort = _iokit.IOMasterPort
IOMasterPort.argtypes = [ basetypes.mach_port_t, ctypes.POINTER(basetypes.mach_port_t) ]
IOMasterPort.restype = basetypes.kern_return_t

IOObjectConformsTo = _iokit.IOObjectConformsTo
IOObjectConformsTo.argtypes = [ io_object_t, const_io_name_t ]
IOObjectConformsTo.restype = basetypes.boolean_t

IOObjectRelease = _iokit.IOObjectRelease
IOObjectRelease.argtypes = [ io_object_t ]
IOObjectRelease.restype = basetypes.kern_return_t

IORegistryEntryCreateIterator = _iokit.IORegistryEntryCreateIterator
IORegistryEntryCreateIterator.argtypes = [
    io_registry_entry_t, const_io_name_t, IOOptionBits, ctypes.POINTER(io_iterator_t) ]
IORegistryEntryCreateIterator.restype = basetypes.kern_return_t

IORegistryEntryCreateCFProperty = _iokit.IORegistryEntryCreateCFProperty
IORegistryEntryCreateCFProperty.argtypes = [
    io_registry_entry_t, corefoundation.CFStringRef, corefoundation.CFAllocatorRef, IOOptionBits ]
IORegistryEntryCreateCFProperty.restype = corefoundation.CFTypeRef

IORegistryEntryGetName = _iokit.IORegistryEntryGetName
IORegistryEntryGetName.argtypes = [ io_registry_entry_t, mutable_io_name_t ]
IORegistryEntryGetName.restype = basetypes.kern_return_t

IOServiceGetMatchingServices = _iokit.IOServiceGetMatchingServices
IOServiceGetMatchingServices.argtypes = [
    basetypes.mach_port_t, corefoundation.CFDictionaryRef, ctypes.POINTER(io_iterator_t) ]
IOServiceGetMatchingServices.restype = basetypes.kern_return_t

IOServiceMatching = _iokit.IOServiceMatching
IOServiceMatching.argtypes = [ ctypes.c_char_p ]
IOServiceMatching.restype = corefoundation.CFMutableDictionaryRef

# helpers
class IOIterator(object):
    """Adapt an io_iterator_t into a Python iterator

    Optionally, the iteration results can be filtered by providing a
    filter function.

    Returned objects will be autoreleased.
    """

    def __init__(self, io_iterator, filter_func=None):
        self._io_iterator = io_iterator
        self._filter_func = filter_func

    def __iter__(self):
        return self

    def __next__(self):
        next_object = IOIteratorNext(self._io_iterator).autorelease()
        while next_object:
            if not self._filter_func or self._filter_func(next_object):
                return next_object
            next_object = IOIteratorNext(self._io_iterator)
        raise StopIteration()

    def next(self):
        return self.__next__()
