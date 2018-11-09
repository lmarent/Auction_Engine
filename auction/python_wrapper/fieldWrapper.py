from ctypes import c_double
from ctypes import cdll
lib = cdll.LoadLibrary('/usr/local/lib/ipap/libipap.so')


class Foo(object):
    def __init__(self):
        self.obj = lib.Foo_new()

    def bar(self):
        lib.Foo_bar(self.obj)
    
    def doubleme(self, intnumber):
        return lib.Foo_doubleme(self.obj, intnumber)
     
    def printfloat(self, doublenumber):
        lib.Foo_printfloat(self.obj, c_double(doublenumber))
