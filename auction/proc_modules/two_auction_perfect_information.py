from foundation.module import Module
from foundation.config_param import ConfigParam

from utils.auction_utils import log

from proc_modules.proc_module import ProcModule
from proc_modules.proc_module import AllocProc

from typing import Dict


class TwoAuctionPerfectInformation(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(TwoAuctionPerfectInformation, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_params = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0
        self.proc_module = ProcModule()

    def init_module(self, config_params: Dict[str, ConfigParam]):
        """
        Initializes the module

        :param config_params: dictionary with the given configuration parameters
        """
        self.logger.debug('in init_module')
        self.config_params = config_params
        self.domain = config_params['domainid']

    def destroy_module(self):
        """
        method to be executed when destroying the class
        :return:
        """
        self.logger.debug('in destroy_module')
