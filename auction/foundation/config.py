# config.py
import pathlib
import yaml
from foundation.singleton import Singleton
from foundation.config_param import ConfigParam

class Config(metaclass=Singleton):

    def __init__(self, file_name=None):
        base_dir = pathlib.Path(__file__).parent.parent
        if file_name:
            self.config_path = base_dir / 'config' / file_name
        else:
            self.config_path = base_dir / 'config' / 'auction_agent.yaml'
        self.config = None

    def get_config(self):
        """
        Gets configuration parameters.
        :return:
        """
        if self.config is None:
            with open(self.config_path) as f:
                self.config = yaml.load(f)
            return self.config
        else:
            return self.config

    def get_items(self, config_group:str, module:str) -> list:
        """
        Gets the configuration paramaters associated with a config group
        :param config_group  configuration group to find.
        :param module        module parameters to find.
        :return:
        """
        ret = []
        if config_group in self.get_config():
            conf_grp_map = self.get_config()[config_group]
            ret_list = conf_grp_map[module]
            for param in ret:
                ret.append(ConfigParam(ret[param]['Name'], ret[param]['Type'], ret[param]['Value']))
        else:
            raise ValueError("configuration group {0} was not found in config file".format(config_group))

        return ret

    def get_config_param(self, config_group: str, param: str) -> str:
        """
        Gets the configuration paramaters associated with a config group
        :param config_group  configuration group to find.
        :param param         parameter to find.
        :return: param as string
        """
        ret = []
        if config_group in self.get_config():
            conf_grp_map = self.get_config()[config_group]
            if param in conf_grp_map:
                return conf_grp_map[param]
            else:
                raise ValueError("configuration param {0} not defined in config param {1}".format(
                            param, config_group))
        else:
            raise ValueError("configuration group {0} was not found in config file".format(config_group))

        return ret
