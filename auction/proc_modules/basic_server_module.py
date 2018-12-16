from foundation.module import Module
from datetime import datetime


class basic_server_module(Module):


    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        super(basic_server_module,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = []

    def init_module(self, config_param_list:list):
        self.config_param_list = config_param_list

    def destroy_module(self):
        print ('destroying the module')

    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict) -> dict:
        print('in execute')
        return {}

    def execute_user(self, request_params, auctions: list, start:datetime, stop:datetime) -> list:
        pass

    def reset(self):
        print('reset')