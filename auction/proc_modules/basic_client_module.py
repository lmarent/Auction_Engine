from foundation.module import Module
from datetime import datetime


class basic_client_module(Module):


    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        super(basic_client_module,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = []

    def init_module(self, config_param_list:list):
        self.config_param_list = config_param_list

    def destroy_module(self):
        print ('destroying the module')

    def execute_user(self, request_params, auctions: list, start:datetime, stop:datetime) -> list:
        print('in execute user')
        return {}

    def reset(self):
        print('reset')