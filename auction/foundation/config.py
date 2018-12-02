# config.py
import pathlib
import yaml
from foundation.singleton import Singleton

class Config(metaclass=Singleton):

    def __init__(self):
        base_dir = pathlib.Path(__file__).parent.parent
        self.config_path = base_dir / 'config' / 'auction_cli.yaml'
        self.config = None

    def get_config(self):
        if self.config == None:
            with open(self.config_path) as f:
                self.config = yaml.load(f)
            return self.config
        else:
            return self.config
