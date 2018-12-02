from ctypes import cdll
from ctypes import c_int
lib = cdll.LoadLibrary('libipap.so')

class IpapFieldKey:

    def __init__(self, eno=0 , ftype=0 ):
        """

        :param obj:  pointer to the object,otherwise we call the new object.
        :param eno:    enterprise number of type int
        :param ftype:  field type of type int.
        """
        self.obj = lib.ipap_field_key_new(c_int(eno), c_int(ftype))

    def get_eno(self) -> int:
        return lib.ipap_field_key_get_eno(self.obj)

    def get_ftype(self) -> int :
        return lib.ipap_field_key_get_ftype(self.obj)

    def get_key(self) -> str:
        return str(lib.ipap_field_key_get_eno(self.obj)) + '-' + str(lib.ipap_field_key_get_ftype(self.obj))

    def __del__(self):
        if self.obj:
            lib.ipap_field_key_destroy(self.obj)

    def destroy(self):
        lib.ipap_field_key_destroy(self.obj)
