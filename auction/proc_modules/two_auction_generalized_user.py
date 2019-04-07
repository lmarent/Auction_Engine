from foundation.module import Module
from foundation.auction import AuctioningObjectType
from foundation.bidding_object import BiddingObject
from foundation.field_value import FieldValue
from foundation.module import ModuleInformation

from utils.auction_utils import log
from proc_modules.proc_module import ProcModule

from datetime import datetime
from typing import Dict, List


class TwoAuctionGeneralizedUser(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(TwoAuctionGeneralizedUser, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.proc_module = ProcModule()
        self.domain = 0
        self.logger = log().get_logger()

    def init_module(self, config_params: dict):
        self.config_param_list = config_params
        self.domain = config_params['domainid']

    def destroy_module(self):
        pass

    def check_parameters(self, request_params):
        required_fields = set()
        required_fields.add(self.proc_module.field_def_manager.get_field("quantity"))
        required_fields.add(self.proc_module.field_def_manager.get_field("unitbudget"))
        required_fields.add(self.proc_module.field_def_manager.get_field("maxvalue"))

        for field in required_fields:
            if field['key'] not in request_params:
                raise ValueError("basic module: ending check - it does not pass the check, \
                                 field not included {0}".format(field['key']))

    def create_bidding_object(self, auction_key: str, quantity: float, unit_budget: float,
                              unit_price: float, start: datetime, stop: datetime) -> BiddingObject:
        """
        Create bidding objects
        :param auction_key:
        :param quantity:
        :param unit_budget:
        :param unit_price:
        :param start:
        :param stop:
        :return:
        """
        self.logger.debug("starting create bidding object")
        if unit_budget < unit_price:
            unit_price = unit_budget

        # build the elements of the bidding object
        elements = dict()
        config_elements = dict()
        record_id = "record_1"
        self.proc_module.insert_string_field("recordid", record_id, config_elements)

        if unit_price > unit_budget:
            unit_price = unit_budget

        self.proc_module.insert_float_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", unit_price, config_elements)
        elements[record_id] = config_elements

        # build the options (time intervals)
        options = dict()
        option_id = 'option_1'
        config_options = dict()
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        bidding_object = BiddingObject(auction_key, bidding_object_key,
                                       AuctioningObjectType.BID, elements, options)

        self.logger.debug("ending create bidding object")
        return bidding_object

    def execute(self, request_params: Dict[str, FieldValue], auction_key: str,
                start: datetime, stop: datetime, bids: dict) -> list:
        return []

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        """

        :param request_params:
        :param auctions:
        :param start:
        :param stop:
        :return:
        """

        self.logger.debug("two auction generalized module: start execute with # {0} of auctions".format(len(auctions)))
        list_return: List[BiddingObject] = []
        self.check_parameters(request_params)
        if len(auctions) > 0:

            # Get the total money and budget and divide them by the number of auctions
            budget = self.proc_module.get_param_value("unitbudget", request_params)
            max_unit_valuation = self.proc_module.get_param_value("maxvalue", request_params)
            quantity = self.proc_module.get_param_value("quantity", request_params)

            for auction_key in auctions:
                bidding_object = self.create_bidding_object(auction_key, quantity, budget,
                                                            max_unit_valuation, start, stop)
                list_return.append(bidding_object)

        self.logger.debug("two auction generalized module: end execute")
        return list_return

    def reset(self):
        print('reset')

    def get_module_info(self, option: ModuleInformation) -> str:
        self.logger.debug("two auction generalized module: start getModuleInfo")

        if option == ModuleInformation.I_MODNAME:
            return "Two Auction Generalized User procedure"
        elif option == ModuleInformation.I_ID:
            return "twoauctiongeneralizeduser"
        elif option == ModuleInformation.I_VERSION:
            return "0.1"
        elif option == ModuleInformation.I_CREATED:
            return "2016/03/08"
        elif option == ModuleInformation.I_MODIFIED:
            return "2016/03/08"
        elif option == ModuleInformation.I_BRIEF:
            return "The auction just choose the minimum between the budget and unit price given as parameters"
        elif option == ModuleInformation.I_VERBOSE:
            return "The auction just choose the minimum between the budget and unit price given as parameters"
        elif option == ModuleInformation.I_HTMLDOCS:
            return "http://www.uniandes.edu.co/... "
        elif option == ModuleInformation.I_PARAMS:
            return "IPAP_FT_QUANTITY, IPAP_FT_UNITBUDGET, IPAP_FT_MAXUNITVALUATION, IPAP_FT_STARTSECONDS, \
                    IPAP_FT_ENDSECONDS"
        elif option == ModuleInformation.I_RESULTS:
            return "A bidding for the request"
        elif option == ModuleInformation.I_AUTHOR:
            return "Andres Marentes"
        elif option == ModuleInformation.I_AFFILI:
            return "Universidad de los Andes, Colombia"
        elif option == ModuleInformation.I_EMAIL:
            return "la.marentes455@uniandes.edu.co"
        elif option == ModuleInformation.I_HOMEPAGE:
            return "http://homepage"
        else:
            return ''
