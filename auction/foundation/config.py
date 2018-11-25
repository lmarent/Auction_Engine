# config.py
import pathlib
import yaml
from foundation.singleton import Singleton

class Config(metaclass=Singleton):

    def __init__(self):
        BASE_DIR = pathlib.Path(__file__).parent.parent
        self.config_path = BASE_DIR / 'config' / 'auction_cli.yaml'
        self.config = None

    def get_config(self):
        if self.config == None:
            with open(self.config_path) as f:
                config = yaml.load(f)
            return config
        else:
            return self.config
