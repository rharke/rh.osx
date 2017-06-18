Python bindings to access native macOS APIs

Specifics
=========

I created this library to provide access to native macOS APIs to other Python code I've written.
It uses ``ctypes`` to bind to the underlying C APIs, and generally just exposes the APIs 'as is'
without attempting to Python-ify them.

It does, however, provide several facilities to make working with the APIs a little easier, but they
are entirely optional. Several types (e.g. ``CFTypeRef``, ``io_object_t``) have an ``autorelease()``
method which will automatically call the appropriate function to release the object when the Python
object holding the reference is destroyed.

Additionally, strings can be automatically converted to/from ``CFStringRef``. The aforementioned
autorelease method is used to ensure that the ephemeral ``CFStringRef`` does not leak.

There is an ``IOIterator`` class which can adapt an ``io_iterator_t`` into a Python iterator.

The bindings are NOT comprehensive and I generally just add stuff as I need it.

The code is tested with Python 2.7 and 3.6.

Examples
========

    >>> from rh.osx import corefoundation
    >>> string_copy = corefoundation.CFStringCreateCopy(None,
    ... """The Python string object is automatically converted to a CFStringRef.
    ... The returned CFStringRef copy will automatically be released.""").autorelease()
    >>> print(str(string_copy))
    The Python string object is automatically converted to a CFStringRef.
    The returned CFStringRef copy will automatically be released.

License
=======

This library is distributed under the MIT license, as described in the LICENSE file.
