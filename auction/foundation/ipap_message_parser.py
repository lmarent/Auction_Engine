from python_wrapper.ipap_template import IpapTemplate, ObjectType, TemplateType
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_message import IpapMessage

from foundation.field_def_manager import FieldDefManager


class IpapMessageParser:

    def __init__(self, domain: int):
        self.domain = domain
        self.field_def_manager = FieldDefManager()

    @staticmethod
    def parse_name(id_auction: str) -> (str, str):
        """
        Parses an object name (auction or bid).

        :param id_auction: Identifier formated as 'setname.objectname'
        :return: (set_name, name)
        """
        if len(id_auction) == 0:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id_auction))

        ids = id_auction.split(".")

        if len(ids) == 0:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id_auction))

        elif len(ids) == 1:
            set_name = ""
            name = ids[0]
            return set_name, name

        elif len(ids) == 2:
            set_name = ids[0]
            name = ids[1]
            return set_name, name
        else:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id_auction))

    @staticmethod
    def parse_object_type(s_type: str) -> ObjectType:
        """
        Parses the type of bidding object

        :param s_type: object type represented as string
        :return:
        """
        if (s_type == "auction") or (s_type == "0"):
            obj_type = ObjectType.IPAP_AUCTION
            return obj_type

        elif (s_type == "bid") or (s_type == "1"):
            obj_type = ObjectType.IPAP_BID
            return obj_type

        elif (s_type == "ask") or (s_type == "2"):
            obj_type = ObjectType.IPAP_ASK
            return obj_type

        elif (s_type == "allocation") or (s_type == "3"):
            obj_type = ObjectType.IPAP_ALLOCATION
            return obj_type

        else:
            raise ValueError("Bidding Object Parser Error: invalid bidding object type {0}".format(s_type))

    @staticmethod
    def parse_template_type(obj_type: ObjectType, templ_type: str) -> TemplateType:
        """
        Parses a template type

        :param obj_type: object type for which this template type belongs to
        :param templ_type: template type represented as string
        :return: template type
        """
        if obj_type == ObjectType.IPAP_AUCTION:
            if templ_type == "data":
                return TemplateType.IPAP_SETID_AUCTION_TEMPLATE
            elif templ_type == "option":
                return TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE

        elif obj_type == ObjectType.IPAP_BID:
            if templ_type == "data":
                return TemplateType.IPAP_SETID_BID_OBJECT_TEMPLATE
            elif templ_type == "option":
                return TemplateType.IPAP_OPTNS_BID_OBJECT_TEMPLATE

        elif obj_type == ObjectType.IPAP_ASK:
            if templ_type == "data":
                return TemplateType.IPAP_SETID_ASK_OBJECT_TEMPLATE
            elif templ_type == "option":
                return TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE

        elif obj_type == ObjectType.IPAP_ALLOCATION:
            if templ_type == "data":
                return TemplateType.IPAP_SETID_ALLOC_OBJECT_TEMPLATE
            elif templ_type == "option":
                return TemplateType.IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE

        raise ValueError("Bidding Object Parser Error: invalid template type")

    @staticmethod
    def read_template(message: IpapMessage, template_type: TemplateType) -> IpapTemplate:
        """
        Reads a template type from a message.

        :return: Ipap Template
        """
        temp_list = message.get_template_list()
        for id_template in temp_list:
            template = message.get_template_object(id_template)
            if template.get_type() == template_type:
                return template

        raise ValueError("Template not found")

    @staticmethod
    def read_data_records(message: IpapMessage, templ_id: int) -> list:
        """
        Reads the data record list from a message

        templ_id : template identifier.
        :return: list of data records within the message.
        """
        size = message.get_data_record_size()
        list_return = []
        for i in range(0, size):
            data_record = message.get_data_record_at_pos(i)
            if data_record.get_template_id() == templ_id:
                list_return.append(data_record)
        return list_return


    def get_domain(self) -> int:
        """
        Get the domaid id used by the ipapmessage.The domain id corresponds to the agent identifier.
        :return: domain
        """
        return self.domain
