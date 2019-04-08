from ctypes import cdll
from ctypes import c_double
from ctypes import c_int
from ctypes import byref

lib = cdll.LoadLibrary('libtwoauctiongen.so')


class TwoAuctionMechanismGeneralized:

    def __init__(self, obj=None):

        if obj:
            self.obj = obj
        else:
            self.obj = lib.two_auction_mechanism_generalized_new()

    def zero_in(self, nh: int, nl: int, bh: float,
                bl: float, kh: float, kl: float, rph: float, rpl: float, q: float,
                x: float, y: float) -> (int, float, float):

        zeroin = lib.two_auction_mechanism_generalized_zero_in
        zeroin.restype = c_int

        x_to_send = c_double(x)
        y_to_send = c_double(y)

        out = lib.two_auction_mechanism_generalized_zero_in(self.obj, c_int(nh), c_int(nl), c_double(bh), c_double(bl),
                                                            c_double(kh), c_double(kl), c_double(rph), c_double(rpl),
                                                            c_double(q), byref(x_to_send), byref(y_to_send))

        return out, x_to_send.value, y_to_send.value

    def __del__(self):
        if self.obj:
            lib.two_auction_mechanism_generalized_destroy(self.obj)
