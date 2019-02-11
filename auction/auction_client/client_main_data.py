from foundation.singleton import Singleton
from foundation.config import Config
from foundation.parse_format import  ParseFormats

class ClientMainData(metaclass=Singleton):

    def __init__(self):

        self.domain = Config().get_config_param('Main','Domain')
        use_ipv6 = Config().get_config_param('Main','UseIPv6')
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        self.ip_address6 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V6'))
        self.destination_address6 = ParseFormats.parse_ipaddress(
                            Config().get_config_param('Main','DefaultDestinationAddr-V6'))
        self.ip_address4 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V4'))
        self.destination_address4 = ParseFormats.parse_ipaddress(
                            Config().get_config_param('Main','DefaultDestinationAddr-V4'))

        # Gets default ports (origin, destination)
        self.source_port = ParseFormats.parse_uint16(Config().get_config_param('Main','DefaultSourcePort'))
        self.destination_port = ParseFormats.parse_uint16(
                                Config().get_config_param('Main','DefaultDestinationPort'))
        self.protocol = ParseFormats.parse_uint8( Config().get_config_param('Main','DefaultProtocol'))
        self.life_time = ParseFormats.parse_uint8( Config().get_config_param('Main','LifeTime'))
