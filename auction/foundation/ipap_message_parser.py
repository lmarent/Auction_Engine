from python_wrapper.ipap_template import IpapTemplate, object_type, template_type
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_message import IpapMessage

from foundation.field import Field
from foundation.field import MatchFieldType
from foundation.field_value import FieldValue
from foundation.field_def_manager import FieldDefManager

class IpapMessageParser:

    def __init__(self, domain):
        self.domain = domain

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

    def read_data_records(self, message : IpapMessage, templ_id : int) -> list:
        """
        Reads the data record list from a message

        :return: list fo data records within the message.
        @:raises ValueError when a data record is not found.
        """
        size = message.get_data_record_size()
        list_return = []
        for i in range(0,size):
            data_record = message.get_data_record_at_pos(i)
            list_return.append(data_record)
        return list_return


    def find_field(self, eno : int, ftype : int ):
        """
        Finds a field by eno and ftype within the list of fields.

        :return: field definition
        """
        field_def_manager = FieldDefManager()
        return field_def_manager.get_field_by_code(eno,ftype)


    def find_field_by_name(self, name : str):
        """
        Find a field by name within the list of fields.

        :return:
        """
        field_def_manager = FieldDefManager()
        return field_def_manager.get_field(name)


    def parse_field_value(self, value : str, field_type : str, field : Field ):
        """
        parses a field value and let the alue parsed in field.

        :return: Nothing
        """
        field_def_manager = FieldDefManager()

        field.cnt_values = 0
        field.value.clear()

        if value.__eq__("*"):
            field.match_type = MatchFieldType.FT_WILD
            field.cnt_values = 1

        elif "-" in value:
            field.match_type = MatchFieldType.FT_RANGE
            values = value.split("-")
            if len(values) != 2:
                raise ValueError("The value given must have a valid range format: value1-value2")
            for val in values:
                value_translated = field_def_manager.get_field_value(field.type,val)
                if value_translated is not None:
                    field.value.append(FieldValue(MatchFieldType.FT_WILD,value_translated))
                else:
                    field.value.append(FieldValue(MatchFieldType.FT_WILD, val))
                field.cnt_values = field.cnt_values + 1

        elif "," in value:
            values = value.split(",")
            for val in values:
                value_translated = field_def_manager.get_field_value(field.type,val)
                if value_translated is not None:
                    field.value.append(FieldValue(MatchFieldType.FT_SET,value_translated))
                else:
                    field.value.append(FieldValue(MatchFieldType.FT_SET, val))
                field.cnt_values = field.cnt_values + 1

        else:
            value_translated = field_def_manager.get_field_value(field.type, val)
            if value_translated is not None:
                field.value.append(FieldValue(MatchFieldType.FT_EXACT, self.lookup(field_val_list,value, field.type)))
            else:
                field.value.append(FieldValue(MatchFieldType.FT_EXACT,value))
            field.cnt_values = 1


    def get_misc_val(self):
        """
        Gets a value by name from the misc rule attributes

        :return:
        """
        # TODO: To Implement.
        pass

    def get_domain(self) -> int:
        """
        Get the domaid id used by the ipapmessage.The domain id corresponds to the agent identifier.
        :return: domain
        """
        return self.domain
