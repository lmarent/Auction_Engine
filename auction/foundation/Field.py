from enum import Enum

class DataType(Enum):
    INVALID1 = -1
    EXPORTEND = 0
    LIST = 2
    LISTEND = 3
    CHAR = 4
    INT8 = 5
    INT16 = 6
    INT32 = 7
    INT64 = 8
    UINT8 = 9
    UINT16 = 10
    UINT32 = 11
    UINT64 = 12
    STRING = 13
    BINARY = 14
    IPV4ADDR = 15
    IPV6ADDR = 16
    FLOAT = 17
    DOUBLE = 18
    INVALID2 = 19

class FieldType(Enum):
    FT_EXACT = 0
    FT_RANGE = 1
    FT_SET = 2
    FT_WILD= 3

