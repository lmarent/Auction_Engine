from enum import Enum
from foundation.field_value import FieldValue

class DataType(Enum):
    """
    Datatypes being used for fields.
    """
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

class MatchFieldType(Enum):
    """
    Match Field value type.The following is the list of value types:
    EXACT --> 0 It is put on the first position of the value list
    RANGE --> 1 It is put on the first and second positions
                of the value list. First position is the minimum value,
                second position is the maximum value
    SET   --> 2 The set of values area inserted in the list.
    WILD  --> 3 No value.
    """
    FT_EXACT = 0
    FT_RANGE = 1
    FT_SET = 2
    FT_WILD= 3

class Fieldefinition:
    """
    Field definition for relating a field of the auctio system with a field
    in an Ipap Message
    """
    def __init__(self, name : str, type :str, length : int, eno :int , ftype: int ):
        """
        Constructor for the class
        :param name:    field's name
        :param type:    field's type in string
        :param length:  field's length
        :param eno:     enterprise number of the field
        :param ftype:   field identifier used in the ipap_message.
        """
        self.name = name
        self.type = type
        self.length = length
        self.eno = eno
        self.ftype = ftype

class Field:
    """
    This class represents a field value given as parameter by the user.

    Attributes
     --------
    name: field's name
    type: Field's type
    match_type: the match type (exact, range,etc...)
    length: lenght of the field value
    cnt_values: number of field values
    """

    def __init__(self, name=None, type=None, match_type=MatchFieldType.FT_WILD, length=0, cnt_values=0):
        self.name = name
        self.type
        self.match_type = match_type
        self.length = length
        self.cnt_values = cnt_values
        self.value = []

    def parse_field_value(self, value: str):
        """
        Parses a value in string.
        :param value: value in string
        """
        self.cnt_values = 0
        self.value.clear()

        if value.__eq__("*"):
            self.match_type = MatchFieldType.FT_WILD
            self.cnt_values = 1

        elif "-" in value:
            self.match_type = MatchFieldType.FT_RANGE
            values = value.split("-")
            if len(values) != 2:
                raise ValueError("The value given must have a valid range format: value1-value2")
            for val in values:
                self.value.append(FieldValue(MatchFieldType.FT_WILD,val))
                self.cnt_values = self.cnt_values + 1

        elif "," in value:
            values = value.split(",")
            for val in values:
                self.value.append(FieldValue(MatchFieldType.FT_SET,val))
                self.cnt_values = self.cnt_values + 1

        else:
            self.value.append(FieldValue(MatchFieldType.FT_EXACT, value))
            self.cnt_values = 1
