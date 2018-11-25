from python_wrapper.ipap_template import IpapTemplate, object_type, template_type
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_message import IpapMessage

class IpapMessageParser:

    def __init__(self):
        self.domain =

    def parse_name(self, id : str) -> (str, str):
        """
        Parses an object name (auction or bid).

        :param id: Identifier formated as 'setname.objectname'
        :return: (set_name, name)
        """
        if len(id) == 0:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id))

        ids = id.split(".")

        if len(ids) == 0:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id))

        elif len(ids) == 1:
            set_name = ""
            name = ids[0]
            return (set_name,name)

        elif len(ids) == 2:
            set_name = ids[0]
            name = ids[1]
            return (set_name,name)
        else:
            raise ValueError("malformed identifier {0}, use <identifier> or <set>.<identifier> ".format(id))

    def parse_object_type(self, stype : str) -> object_type:
        """
        Parses the type of bidding object

        :param stype: object type represented as string
        :return:
        """

        type = object_type.IPAP_INVALID

        if (stype == "auction") or (stype == "0"):
            type = object_type.IPAP_AUCTION

        elif (stype == "bid") or (stype == "1"):
            type = object_type.IPAP_BID

        elif (stype == "ask") or (stype == "2"):
            type = object_type.IPAP_ASK

        elif (stype == "allocation") or (stype == "3"):
            type = object_type.IPAP_ALLOCATION

        else:
            raise ValueError("Bidding Object Parser Error: invalid bidding object type {0}".format(stype))

        return type


    def parse_template_type(self, obj_type : object_type, templ_type : str ) -> template_type:
        """
        Parses a template type

        :param obj_type: object type for which this template type belongs to
        :param templ_type: template type represented as string
        :return: template type
        """
        if obj_type == object_type.IPAP_BID:
            if templ_type == "data":
                return template_type.IPAP_SETID_BID_OBJECT_TEMPLATE
            elif templ_type == "option":
                return template_type.IPAP_OPTNS_BID_OBJECT_TEMPLATE

        elif obj_type == object_type.IPAP_ASK:
            if templ_type == "data":
                return template_type.IPAP_SETID_ASK_OBJECT_TEMPLATE
            elif templ_type == "option":
                return template_type.IPAP_OPTNS_ASK_OBJECT_TEMPLATE

        elif obj_type == object_type.IPAP_ALLOCATION:
            if templ_type == "data":
                return template_type.IPAP_SETID_ALLOC_OBJECT_TEMPLATE
            elif templ_type == "option":
                return template_type.IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE

        raise ValueError("Bidding Object Parser Error: invalid template type")

    def read_template(self, message : IpapMessage) -> IpapTemplate:
        """
        Reads a template type from a message.

        :return: Ipap Template
        """
        tempList = message.get_template_list()
        for id_template in tempList:
            template = message.get_template_object(id_template)
            if template.get_type() == type:
                return template

        return None

    def read_data_record(self) -> IpapDataRecord:
        """
        Redas a data record from a message

        :return:
        """

    def find_value(self, eno : int, ftype : int ):
        """
        Finds a field by eno and ftype within the list of fields.

        :return: field definition
        """



    def find_value_by_name(self, name : str):
        """
        Find a field by name within the list of fields.

        :return:
        """

    def parse_field_value(self):
        """
        parses a field value

        :return:
        """


    def lookup(self, field_val_list : list, field):
        """
        lookup field value

        :return:
        """
        

    def get_misc_val(self):
        """
        Gets a value by name from the misc rule attributes

        :return:
        """

    def get_domain(self) -> int:
        """
        Get the domaid id used by the ipapmessage.The domain id corresponds to the agent identifier.
        :return: domain
        """

    def is_field_included(self):
        """

        :return:
        """