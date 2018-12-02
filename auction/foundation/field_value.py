from foundation.specific_field_value import SpecificFieldValue
from foundation.field_def_manager import FieldDefManager
from enum import Enum


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

class FieldDefinition:
    """
    Field definition for relating a field of the auction system with a field
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


class FieldValue:
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
        self.type = type
        self.match_type = match_type
        self.length = length
        self.cnt_values = cnt_values
        self.value = []

    def _parse_field_value_exact(self, value: str):
        """
        Parsers the value when it is only one value
        :param value: value to be parsed
        :param field: field where the values area going to be assigned.
        """
        try:
            value_translated = FieldDefManager().get_field_value(self.type, value)
            self.value.append(FieldValue(self.type,value_translated))

        except ValueError:
            self.value.append(FieldValue(self.type, value))

        self.cnt_values = 1

    def _parse_field_value_range(self, value: str):
        """
        Parses the value when it is range.

        :param value: value to parse.
        :param field: field where the values area going to be assigned.
        :return:
        """
        self.match_type = MatchFieldType.FT_RANGE
        values = value.split("-")
        if len(values) != 2:
            raise ValueError("The value given must have a valid range format: value1-value2")
        for val in values:
            try:
                value_translated = FieldDefManager().get_field_value(self.type, val)
                self.value.append(FieldValue(self.type, value_translated))

            except ValueError:
                self.value.append(FieldValue(self.type,val))

            self.cnt_values = self.cnt_values + 1

    def _parse_field_value_list(self, value: str):
        """
        Parsers a value when the string correspond to a list
        :param value: string value to parse
        :param field: field where the values area going to be assigned.
        """
        values = value.split(",")
        for val in values:
            try:
                value_translated = FieldDefManager().get_field_value(self.type, val)
                self.value.append(FieldValue(self.type,value_translated))
            except ValueError:
                self.value.append(FieldValue(self.type, val))

            self.cnt_values = self.cnt_values + 1

    def parse_field_value(self, value: str):
        """
        parses a field value and let the value parsed in field.

        :param value string to parse
        :param field: field where the values area going to be assigned.
        :return: Nothing
        """
        self.cnt_values = 0
        self.value.clear()

        if value.__eq__("*"):
            self.match_type = MatchFieldType.FT_WILD
            self.cnt_values = 0

        elif "-" in value:
            self._parse_field_value_range(value)

        elif "," in value:
            self._parse_field_value_list(value)
        else:
            self._parse_field_value_exact(value)
