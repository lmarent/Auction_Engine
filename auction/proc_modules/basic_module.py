from foundation.module import Module
from foundation.field_value import FieldValue
from datetime import datetime

from typing import Dict


class BasicModule(Module):


    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        super(BasicModule,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}

    def init_module(self, config_param_list:dict):
        print ('in init_module')
        self.config_param_list = config_param_list

    def destroy_module(self):
        print ('in destroy_module')

    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict) -> dict:
        print('in execute')
        return {}

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        print('in execute_user')
        pass

    def reset(self):
        print('in reset')