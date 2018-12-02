

class SpecificFieldValue:
    """
    Class to maintain a specific field value in string representation

    attributes
    ----------
    field_type: str type of the value stored
    value: value stored.
    """

    def __init__(self, field_type=None, value=None):
        self.field_type = field_type
        self.value = value

    def set_field_type(self, field_type : str):
        self.field_type = field_type

    def set_value(self, value: str):
        self.value = value
