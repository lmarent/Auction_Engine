import ipaddress
import datetime
from datetime import timedelta
from decimal import Decimal
from foundation.config import Config


class ParseFormats:
    """
    Class for parse value in string to different types
    """

    @staticmethod
    def parse_long(value: str) -> int:
        """
        Parsers a string which has a long value

        :param value: string
        :return: long
        """
        return int(value)

    @staticmethod
    def parse_ulong(value: str) -> int:
        """
        Parsers a string which has a long value

        :param value: string
        :return: long
        """
        val = int(value)
        if val < 0:
            raise ValueError("unsigned value can't be less than zero")
        else:
            return val

    @staticmethod
    def parse_int(value: str) -> int:
        """
        Parsers a string which has a integer value

        :param value: string
        :return: integer
        """
        return int(value)

    @staticmethod
    def parse_ipaddress(value: str) -> ipaddress:
        """
        Parsers a string  which has a ip address (Ipv4 or Ipv6)

        :param value: string
        :return: ipaddress
        """
        return ipaddress.ip_address(value)

    @staticmethod
    def parse_bool(value: str) -> bool:
        """
        Parsers a string which has a boolean (True, false)

        :param value: Boolean representation
        :return: Boolean
        """
        return bool(value)

    @staticmethod
    def parse_float(value: str) -> float:
        """
        Parsers a string which has a float value

        :param value: string with a float.
        :return: float
        """
        return float(value)

    @staticmethod
    def parse_double(value: str) -> Decimal:
        """
        Parses a string which has a double value
        :param value: string with a double.

        :return: Double
        """
        return Decimal(value)

    @staticmethod
    def parse_time(value: str) -> datetime:
        """
        Parses a string which has a date and time value into datetime.
        :param value: string value

        :return: datetime
        """
        if not value:
            raise ValueError("The given string representing time is invalid")
        if value[0] == "+":
            secs = int(value[1:len(value)])
            time = datetime.datetime.now() + timedelta(seconds=secs)
            return time
        elif value.isnumeric():
            secs = ParseFormats.parse_long(value)
            time = datetime.datetime.fromtimestamp(secs)
            return time
        else:
            config = Config().get_config()
            time = datetime.datetime.strptime(value, config["TimeFormat"])
            return time

    @staticmethod
    def parse_item(c_type: str, value: str):
        """
        Test parsing an item that has a value of a given type

        :param c_type: type to parse
        :param value: value to parse.
        :except ValueError thestring does not have a value of the given type
        """

        if (c_type.lower() == "uint8") or (c_type.lower() == "sint8"):
            ParseFormats.parse_int(value)
        elif (c_type.lower() == "uint16") or (c_type.lower() == "sint16"):
            ParseFormats.parse_long(value)
        elif (c_type.lower() == "uint32") or (c_type == "sint32"):
            ParseFormats.parse_ulong(value)
        elif c_type.lower() == "ipaddr":
            ParseFormats.parse_ipaddress(value)
        elif c_type.lower() == "ip6addr":
            ParseFormats.parse_ipaddress(value)
        elif c_type.lower() == "string":
            pass
        elif c_type.lower() == "bool":
            ParseFormats.parse_bool(value)
        elif c_type.lower() == "float32":
            ParseFormats.parse_float(value)
        elif c_type.lower() == "float64":
            ParseFormats.parse_double(value)
        else:
            raise ValueError("Unsupported type: {0}".format(c_type))
