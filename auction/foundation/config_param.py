from foundation.field_def_manager import DataType
from foundation.parse_format import ParseFormats
from lxml.etree import Element


class ConfigParam:
    """
    A configuration param represents a parameter given to though an auction configuration file.

    attributes
    ----------
    name : str : name of the configuration param
    p_type: str: type of the configuration param
    value : str: value as string.
    """
    def __init__(self, name: str=None, p_type: DataType=None, value: str=None):
        self.name = name
        self.type = p_type
        self.value = value

    def get_name(self) -> str:
        """
        Returns the name of the configuration param
        :return: str: name
        """
        return self.name

    def get_type(self) -> DataType:
        """
        Returns the type of the configuration param
        :return: DataType: type
        """
        return self.type

    def get_value(self):
        """
        Returns the value of the configuration param
        :return: str: value
        """
        return self.value

    def parse_config_item(self, item: Element):
        """
        Parse a configuration item from xml

        :param item: item to be parsed.
        :return
        """
        c_name = item.get("NAME")
        c_value = item.text
        if not c_name:
            raise ValueError("The xml has a preference with no name")

        if not c_value:
            raise ValueError("The xml has a preference with no value")

        self.name = c_name.lower()
        self.value = c_value

        c_type = item.get("TYPE")
        if c_type:
            self.type = ParseFormats.parse_type(c_type.lower())
        else:
            self.type = DataType.STRING

        ParseFormats.parse_item(self.type, self.value)
