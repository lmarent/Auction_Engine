from python_wrapper.ipap_field_type import IpapFieldType
from python_wrapper.ipap_field import IpapField
from ctypes import pointer
ftype = IpapFieldType()
ftype.eno =10
ftype.ftype = 10
ftype.length = 10
ftype.name= b"casa"
ftype.xmlname= b"casa"
ftype.documentation= b"casa"


ipap_field = IpapField(None)
ipap_field2 = IpapField(ftype)