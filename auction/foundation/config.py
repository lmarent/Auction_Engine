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
            self.config_path = base_dir / 'config' / 'auction_cli.yaml'
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

        return ret

