from foundation.auction import Auction
from foundation.bidding_object import BiddingObject
from foundation.auction_process_object import AuctionProcessObject
from foundation.config import Config
from foundation.ipap_message_parser import IpapMessageParser
from foundation.module_loader import ModuleLoader
from foundation.auctioning_object import AuctioningObjectType
from foundation.field_def_manager import FieldDefManager
from foundation.module import Module
from foundation.config_param import ConfigParam
from foundation.config_param import DataType
from foundation.singleton import Singleton
from foundation.field_value import FieldValue


from datetime import datetime
from enum import Enum
from typing import List

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_data_record import IpapDataRecord

from utils.auction_utils import log


class AgentFieldSet(Enum):
    """
    States throughout which can pass the auctioning object.
    """
    SESSION_FIELD_SET_NAME = 0
    REQUEST_FIELD_SET_NAME = 1


class AuctionProcess(AuctionProcessObject):
    """
    This object represents an auction which is going to be executed. It Contains the auction definition,
    its parameters and participating bidding objects.
    """

    def __init__(self, key: str, module: Module, auction: Auction, config_dict: dict):
        """
        Creates the auction process.
        :param key: unique key to identify the auction process
        :param module: module used to execute the auction
        :param auction: auction that is going to be executed
        :param config_dict: parameters
        """
        super(AuctionProcess, self).__init__(key, module)
        self.auction = auction
        self.bids = {}
        self.config_params = {}

        for config_param_name in config_dict:
            config_param = config_dict[config_param_name]
            field_value = FieldValue()
            field_value.parse_field_value_from_config_param(config_param)
            self.config_params[config_param_name] = field_value

    def insert_bid(self, bid: BiddingObject):
        """
        Inserts a bidding object of type bid in the auction process.

        :param bid: bid to insert/.
        :return:
        """
        if bid.get_key() not in self.bids:
            self.bids[bid.get_key()] = bid
        else:
            raise ValueError("Bid is already inserted in the AuctionProcess")

    def get_module(self) -> Module:
        """
        Gets the module associated with the auction process

        :return: Module
        """
        return self.module

    def get_config_params(self) -> dict:
        """
        Gets config params
        :return:
        """
        return self.config_params

    def get_bids(self) -> dict:
        """
        Gets teh bids registered in the action process
        :return: dictionary with all bids
        """
        return self.bids


class AuctionProcessor(IpapMessageParser, metaclass=Singleton):
    """
    This class manages and executes algorithms for a set of auctions.

    Attributes
    ----------
    """

    def __init__(self, domain: int, module_directory: str=None):
        super(AuctionProcessor, self).__init__(domain)
        self.auctions = {}
        self.config = Config().get_config()
        self.field_sets = {}
        self.logger = log().get_logger()
        self.field_def_manager = FieldDefManager()

        if not module_directory:
            if 'AUMProcessor' in self.config:
                if 'ModuleDir' in self.config['AUMProcessor']:
                    module_directory = self.config['AUMProcessor']['ModuleDir']
                else:
                    ValueError(
                        'Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AumProcessor'))
            else:
                ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

        if 'AUMProcessor' in self.config:
            if 'Modules' in self.config['AUMProcessor']:
                modules = self.config['AUMProcessor']['Modules']
                self.module_loader = ModuleLoader(module_directory, 'AUMProcessor', modules)
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('Modules', 'AumProcessor'))
        else:
            ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

        self.build_field_sets()

    def read_misc_data(self, ipap_template: IpapTemplate, ipap_record: IpapDataRecord) -> dict:
        """
        read the data given in the data record

        :param ipap_template: templete followed by data record
        :param ipap_record: record with the data.
        :return: dictionary with config values.
        """
        config_params = {}
        num_fields = ipap_record.get_num_fields()
        for pos in range(0, num_fields):
            try:

                field_key = ipap_record.get_field_at_pos(pos)

            except ValueError as e:
                self.logger.error(str(e))
                raise e

            try:
                field_def = self.field_def_manager.get_field_by_code(field_key.get_eno(), field_key.get_ftype())
                field = ipap_template.get_field(field_key.get_eno(), field_key.get_ftype())
                config_param = ConfigParam(field_def['name'], field_def['type'],
                                           field.write_value(ipap_record.get_field(
                                               field_key.get_eno(), field_key.get_ftype())))

                config_params[config_param.name.lower()] = config_param
            except ValueError as e:
                self.logger.error("Field with eno {0} and ftype {1} was \
                                    not parametrized".format(str(field_key.get_eno()),
                                                             str(field_key.get_ftype())))
                raise e
        return config_params

    def build_field_sets(self):
        """
        Builds the field sets required for managing message between the server and the agents.
        """
        # Fill data auctions fields
        agent_session = set()
        agent_session.add(IpapFieldKey(self.field_def_manager.get_field('ipversion')['eno'],
                                       self.field_def_manager.get_field('ipversion')['ftype']))
        agent_session.add(IpapFieldKey(self.field_def_manager.get_field('srcipv4')['eno'],
                                       self.field_def_manager.get_field('srcipv4')['ftype']))
        agent_session.add(IpapFieldKey(self.field_def_manager.get_field('srcipv6')['eno'],
                                       self.field_def_manager.get_field('srcipv6')['ftype']))
        agent_session.add(IpapFieldKey(self.field_def_manager.get_field('srcauctionport')['eno'],
                                       self.field_def_manager.get_field('srcauctionport')['ftype']))
        self.field_sets[AgentFieldSet.SESSION_FIELD_SET_NAME] = agent_session

        # Fill option auctions fields
        agent_search_fields = set()
        agent_search_fields.add(IpapFieldKey(self.field_def_manager.get_field('start')['eno'],
                                             self.field_def_manager.get_field('start')['ftype']))
        agent_search_fields.add(IpapFieldKey(self.field_def_manager.get_field('stop')['eno'],
                                             self.field_def_manager.get_field('stop')['ftype']))
        agent_search_fields.add(IpapFieldKey(self.field_def_manager.get_field('resourceid')['eno'],
                                             self.field_def_manager.get_field('resourceid')['ftype']))
        self.field_sets[AgentFieldSet.REQUEST_FIELD_SET_NAME] = agent_search_fields

    def add_auction_process(self, auction: Auction):
        """
        adds a Auction to auction process list

        :param auction: auction to be added
        """
        key = auction.get_key()
        action = auction.get_action()
        module_name = action.name
        module = self.module_loader.get_module(module_name)
        config_params = action.get_config_params()
        if 'domainid' not in config_params:
            config_params['domainid'] = ConfigParam('domainid', DataType.UINT32, str(self.domain))
        action_process = AuctionProcess(key, module, auction, config_params)
        module.init_module(action_process.get_config_params())
        self.auctions[key] = action_process
        return key

    def execute_auction(self, key: str, start: datetime, end: datetime) -> List[BiddingObject]:
        """
        Executes the allocation algorithm for the auction
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions[key]
        module = action_process.get_module()
        allocations = module.execute(action_process.get_config_params(), key, start, end, action_process.get_bids())
        return allocations

    def add_bidding_object_to_auction_process(self, key: str, bidding_object: BiddingObject):
        """
        adds a bidding Object to auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to add
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))
        action_process = self.auctions[key]

        if bidding_object.get_parent_key() != action_process.key:
            raise ValueError("bidding object given {0} is not for the auction {1}".format(
                bidding_object.get_key(), key))

        if bidding_object.get_type() == AuctioningObjectType.BID:
            action_process.insert_bid(bidding_object)
        else:
            raise ValueError("bidding object is not BID type")

    def delete_bidding_object_from_auction_process(self, key: int, bidding_object: BiddingObject):
        """
        deletes a bidding Object from auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to delete
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions[key]
        action_process.bids.pop(bidding_object.get_key(), None)

    def delete_auction_process(self, key: str):
        """
        Deletes an auction process from the list.
        The caller must to remove all loop entries created for this process
        auction.
        :param key key of the auction process
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions.pop(key, None)
        if action_process:
            self.module_loader.release_module(action_process.get_module().get_module_name())

    def get_auction_process(self, key: str) -> AuctionProcess:
        """
        Gets the auction process with the key given
        :param key: key to find
        :return: auction process
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        return self.auctions.get(key)

    def get_set_field(self, set_name: AgentFieldSet):
        """
        Returns teh requested field set

        :param set_name: set of field to get
        :return:
        """
        return self.field_sets[set_name]

    def get_session_information(self, message: IpapMessage) -> dict:
        """
        Gets the session information within the message.

        If the option template is empty, then the returned auction must be zero.
        If the option template has more that a record, then we assume all records have the same session information.

        :param message message from where to extract the session information.
        :return: map of values that identify the session
        """
        session_info = {}
        try:
            templ_opt_auction = self.read_template(message, TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)
            data_records = self.read_data_records(message, templ_opt_auction.get_template_id())
            for data_record in data_records:
                config_items = self.read_misc_data(templ_opt_auction, data_record)
                field_keys = self.get_set_field(AgentFieldSet.SESSION_FIELD_SET_NAME)
                for field_key in field_keys:
                    field = self.field_def_manager.get_field_by_code(
                        field_key.get_eno(), field_key.get_ftype())
                    field_name = field['name'].lower()
                    val = self.get_misc_val(config_items, field_name)
                    session_info[field_name] = val

                break
            return session_info

        except ValueError as e:
            self.logger.error("Error during processing of get session information - error:{0} ".format(str(e)))

    def delete_auction(self, auction: Auction):
        """
        deletes an auction
        :param auction: auction to be deleted
        :return:
        """
        self.delete_auction_process(auction.get_key())

    def insersect(self, start_dttm: datetime, stop_dttm: datetime, resource_id: str) -> list:
        """
        Finds auctions that are executed for the selected resource and for the time range

        :param start_dttm: start of the time interval
        :param stop_dttm: end of the time interval
        :param resource_id: resource for which we want to perform bidding.
        :return: list of applicable auctions
        """
        auctions_ret = []
        for auction_key in self.auctions:
            auction = self.auctions[auction_key].auction
            include = True
            if stop_dttm <= auction.get_start():
                include = False

            if auction.get_stop() <= start_dttm:
                include = False

            if (auction.get_resource_key() != resource_id) \
                    and (resource_id.lower() != "any"):
                include = False

            if include:
                auctions_ret.append(auction)

        return auctions_ret

    def get_applicable_auctions(self, message: IpapMessage) -> list:
        """
        Gets the auctions applicable given the options within the message.

        :rtype: list
        :param message:  message with the options to filter.
        :return: list of application auctions.
        """
        try:
            templ_opt_auction = self.read_template(message, TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)
            data_records = self.read_data_records(message, templ_opt_auction.get_template_id())

            for data_record in data_records:
                config_items = self.read_misc_data(templ_opt_auction, data_record)

                s_start_dttm = self.get_misc_val(config_items, "start")
                ipap_field = templ_opt_auction.get_field(self.field_def_manager.get_field("start")['eno'],
                                                         self.field_def_manager.get_field("start")['ftype'])
                start_dttm = datetime.fromtimestamp(ipap_field.parse(s_start_dttm).get_value_uint64())

                s_stop_dttm = self.get_misc_val(config_items, "stop")
                ipap_field = templ_opt_auction.get_field(self.field_def_manager.get_field("stop")['eno'],
                                                         self.field_def_manager.get_field("stop")['ftype'])
                stop_dttm = datetime.fromtimestamp(ipap_field.parse(s_stop_dttm).get_value_uint64())

                resource_id = self.get_misc_val(config_items, "resourceid")

                auctions = self.insersect(start_dttm, stop_dttm, resource_id)

                return auctions

        except ValueError as e:
            self.logger.error("Error during processing of applicable auctions - error:{0} ".format(str(e)))
