

class FieldValue:


    def __init__(self, field_type=None, length=0, value=None):
        self.field_type = field_type
        self.length = length
        self.value = value

    def set_field_type(self, field_type : str):
        self.field_type = field_type

    def set_lenght(self, length : int):
        self.length = length

    def set_value(self, value: str):
        self.value = value
