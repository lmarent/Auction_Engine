from foundation.singleton import Singleton
from foundation.config import Config
from foundation.parse_format import  ParseFormats

class ServerMainData(metaclass=Singleton):

    def __init__(self):
        self.logger.debug("Stating _load_main_data auction server")

        self.domain = Config().get_config_param('Main','Domain')
        use_ipv6 = Config().get_config_param('Main','UseIPv6')
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if self.use_ipv6:
            self.ip_address6 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V6'))
        else:
            self.ip_address4 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V4'))

        # Gets default ports (origin, destination)
        self.local_port = ParseFormats.parse_uint16(Config().get_config_param('Main','LocalPort'))
        self.protocol = ParseFormats.parse_uint8( Config().get_config_param('Main','DefaultProtocol'))
        self.life_time = ParseFormats.parse_uint8( Config().get_config_param('Main','LifeTime'))
        self.inmediate_start = ParseFormats.parse_bool( Config().get_config_param('Main','ImmediateStart'))

        self.logger.debug("ending _load_main_data")
