from python_wrapper.ipap_template import IpapTemplate, ObjectType, TemplateType
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_message import IpapMessage

from foundation.field import Field
from foundation.field import MatchFieldType
from foundation.field_value import FieldValue
from foundation.field_def_manager import FieldDefManager


class IpapMessageParser:

    def __init__(self, domain):
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

        raise ValueError("Template ")

    @staticmethod
    def read_data_records(message: IpapMessage, templ_id: TemplateType) -> list:
        """
        Reads the data record list from a message

        :return: list of data records within the message.
        @:raises ValueError when a data record is not found.
        """
        size = message.get_data_record_size()
        list_return = []
        for i in range(0, size):
            data_record = message.get_data_record_at_pos(i)
            if data_record.get_template_id() == templ_id:
                list_return.append(data_record)
        return list_return

    def find_field(self, eno: int, ftype: int):
        """
        Finds a field by eno and ftype within the list of fields.

        :return: field definition
        """
        return self.field_def_manager.get_field_by_code(eno, ftype)

    def find_field_by_name(self, name: str):
        """
        Finds a field by name within the list of fields. Field names are case sensitive.

        :return:
        """
        return self.field_def_manager.get_field(name)

    def parse_field_value(self, value: str, field: Field):
        """
        parses a field value and let the alue parsed in field.

        :return: Nothing
        """
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
                try:
                    value_translated = self.field_def_manager.get_field_value(field.type, val)
                    field.value.append(FieldValue(MatchFieldType.FT_WILD, value_translated))
                except ValueError:
                    field.value.append(FieldValue(MatchFieldType.FT_WILD, val))

                field.cnt_values = field.cnt_values + 1

        elif "," in value:
            values = value.split(",")
            for val in values:
                try:
                    value_translated = self.field_def_manager.get_field_value(field.type, val)
                    field.value.append(FieldValue(MatchFieldType.FT_SET, value_translated))
                except ValueError:
                    field.value.append(FieldValue(MatchFieldType.FT_SET, val))

                field.cnt_values = field.cnt_values + 1

        else:
            try:
                value_translated = self.field_def_manager.get_field_value(field.type, value)
                field.value.append(FieldValue(MatchFieldType.FT_EXACT, value_translated))
            except ValueError:
                field.value.append(FieldValue(MatchFieldType.FT_EXACT, value))

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
