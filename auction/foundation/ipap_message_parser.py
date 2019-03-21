from python_wrapper.ipap_template import IpapTemplate, ObjectType, TemplateType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_field import IpapField
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template_container import IpapTemplateContainer

from foundation.field_def_manager import FieldDefManager
from foundation.config_param import ConfigParam
from datetime import datetime


class IpapObjectKey:

    def __init__(self, object_type: ObjectType, key: str):
        self.object_type = object_type
        self.key = key

    def get_object_type(self) -> ObjectType:
        """
        Gets the object type
        :return:
        """
        return self.object_type

    def get_key(self) -> str:
        """
        Gets the objects key
        :return:
        """
        return self.key

    def __eq__(self, other):
        return hasattr(other, 'object_type') and  hasattr(other, 'key') and \
               (self.object_type == other.object_type) and (self.key == other.key)

    def __hash__(self):
        return hash(self.object_type.name + self.key )

    def __lt__(self, other):
        if hasattr(other, 'object_type') and (self.object_type < other.object_type):
            return True
        elif hasattr(other, 'object_type') and (self.object_type > other.object_type):
            return False
        else:
            if hasattr(other, "key"):
                return self.key.__lt__(other.key)
            else:
                return False

    def __ne__(self, other):
        return not (self.__eq__(other))


class IpapMessageParser:

    def __init__(self, domain: int):
        self.domain = domain
        self.field_def_manager = FieldDefManager()
        self.field_container = IpapFieldContainer()
        self.field_container.initialize_reverse()
        self.field_container.initialize_forward()

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

    def include_non_mandatory_fields(self, mandatory_fields: list, config_params: dict, ipap_record: IpapDataRecord):
        """
        Includes non mandatory fields in record

        :param mandatory_fields: list of mandatory fields
        :param config_params: params to include. We should check that are non mandatory fields.
        :param ipap_record: record where we want to include config params
        :return:
        """
        for item in config_params.values():
            field = self.field_def_manager.get_field(item.name)

            # Checks it is not a mandatory field.
            is_mandatory: bool = False
            for mandatory_field in mandatory_fields:
                if mandatory_field.get_eno() == field['eno'] and mandatory_field.get_ftype() == field['ftype']:
                    is_mandatory = True
                    break

            if not is_mandatory:
                # check the field is a valid field for the message
                field_act = self.field_container.get_field(field['eno'], field['ftype'])
                act_f_value = field_act.parse(item.value)
                ipap_record.insert_field(field['eno'], field['ftype'], act_f_value)

    def insert_auction_templates(self, object_type: ObjectType, templates: list,
                                 ipap_template_container: IpapTemplateContainer) -> (IpapTemplate, IpapTemplate):
        """
        Insert auction templates (data and options)
        :param object_type: object type for which we want to insert the templates
        :param templates: list of templates
        :param ipap_template_container: template container where we have to include templates.
        :return: return data and options templates
        """
        data_template = None
        opts_template = None

        # Insert record and options templates for the auction.
        for template in templates:
            if template.get_type() == IpapTemplate.get_data_template(object_type):
                data_template = template
            elif template.get_type() == IpapTemplate.get_opts_template(object_type):
                opts_template = template

        if data_template is None:
            raise ValueError("The message is incomplete Data template was not included")

        if opts_template is None:
            raise ValueError("The message is incomplete Options template was not included")

        # Verify templates
        self.verify_insert_template(data_template, ipap_template_container)
        self.verify_insert_template(opts_template, ipap_template_container)

        return data_template, opts_template

    @staticmethod
    def verify_insert_template(template: IpapTemplate, ipap_template_container: IpapTemplateContainer):
        """
        Verifies and in case of not included before inserts the template given in the template container

        :param template: template to include
        :param ipap_template_container: template container where templates should be verified.
        """
        # Insert templates in case of not created in the template container.
        if ipap_template_container.exists_template(template.get_template_id()):
            template_ret = ipap_template_container.get_template(template.get_template_id())
            if not template_ret.__eq__(template):
                raise ValueError("Data Template {0} given is different from the template already stored".format(
                    template.get_template_id()))

        else:
            ipap_template_container.add_template(template)

    @staticmethod
    def parse_type(s_type: str) -> ObjectType:
        """
        parses the type of bidding object

        :param s_type string representing the type
        :return: object type
        """
        if (s_type == "auction") or (s_type == "0"):
            object_type = ObjectType.IPAP_AUCTION

        elif (s_type == "bid") or (s_type == "1"):
            object_type = ObjectType.IPAP_BID

        elif (s_type == "ask") or (s_type == "2"):
            object_type = ObjectType.IPAP_ASK

        elif (s_type == "allocation") or (s_type == "3"):
            object_type = ObjectType.IPAP_ALLOCATION

        else:
            raise ValueError("Bidding Object Parser Error: invalid bidding object type {0}".format(s_type))

        return object_type

    def get_domain(self) -> int:
        """
        Get the domaid id used by the ipapmessage.The domain id corresponds to the agent identifier.
        :return: domain
        """
        return self.domain

    def read_record(self, template: IpapTemplate, record: IpapDataRecord) -> dict:
        """
        Reads an auction data record
        :param template: record's template
        :param record: data record
        :return: config values
        """
        config_params = {}
        for field_pos in range(0, record.get_num_fields()):
            ipap_field_key = record.get_field_at_pos(field_pos)
            ipap_field_value = record.get_field(ipap_field_key.get_eno(), ipap_field_key.get_ftype())
            f_item = self.field_def_manager.get_field_by_code(ipap_field_key.get_eno(), ipap_field_key.get_ftype())

            ipap_field_value.print_value()

            ipap_field = template.get_field(ipap_field_key.get_eno(), ipap_field_key.get_ftype())
            config_param = ConfigParam(name=f_item['key'],
                                       p_type=f_item['type'],
                                       value=ipap_field.write_value(ipap_field_value))
            config_params[config_param.name] = config_param
        return config_params

    def get_misc_val(self, config_items: dict, item_name: str) -> str:

        if item_name in config_items:
            item: ConfigParam = config_items[item_name]
            value = item.value.lower()
            return value
        else:
            raise ValueError("item with name {0} not found in config items".format(item_name))

    def extract_param(self, config_items: dict, item_name: str) -> ConfigParam:
        """
        Extracts a parameter by name from the list of config items, returns the config param.
        the list config items is altered by removing the parameter.

        :param config_items: config params
        :param item_name: config item name to find.
        :return: the config param
        """
        if item_name in config_items:
            return config_items.pop(item_name)
        else:
            raise ValueError("item with name {0} not found in config items".format(item_name))

    def split(self, ipap_message: IpapMessage) -> (dict, dict, dict):
        """
        parse the ipap message by splitting message data by object key ( Auctions, Bids, Allocations).

        :param ipap_message: message to parse
        :return:
        """
        data_record_count = ipap_message.get_data_record_size()
        templates_included = {}
        object_templates = {}
        object_data_records = {}
        templates_not_related = {}

        for i in range(0, data_record_count):
            data_record = ipap_message.get_data_record_at_pos(i)
            template_id = data_record.get_template_id()
            try:
                template = ipap_message.get_template_object(template_id)

            except ValueError:
                raise ValueError("required template not included in the message")

            templates_included[template_id] = template_id
            templ_type = template.get_type()

            try:
                # Obtain template keys
                data_key = ''
                key_fields = template.get_template_type_key_field(templ_type)
                for key_field in key_fields:
                    field = template.get_field(key_field.get_eno(), key_field.get_ftype())
                    value = data_record.get_field(key_field.get_eno(), key_field.get_ftype())
                    data_key = data_key + field.write_value(value)

                object_type = template.get_object_type(templ_type)
                ipap_object_key = IpapObjectKey(object_type, data_key)

                if ipap_object_key not in object_templates.keys():
                    object_templates[ipap_object_key] = []

                object_templates[ipap_object_key].append(template)

                if ipap_object_key not in object_data_records:
                    object_data_records[ipap_object_key] = []

                object_data_records[ipap_object_key].append(data_record)

            except ValueError as e:
                raise ValueError("error while reading data record - error: {0}", str(e))

        # Copy templates from message that are not related with a record data
        templates = ipap_message.get_template_list()
        for template_id in templates:
            if template_id not in templates_included:
                templates_not_related[template_id] = ipap_message.get_template_object(template_id)

        return object_templates, object_data_records, templates_not_related

    def insert_string_field(self, field_name: str, value: str, record: IpapDataRecord):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(int(field_def['eno']), int(field_def['ftype']))

        # It is required to encode as ascii because the C++ wrapper requires it.
        value_encoded = value.encode('ascii')
        field_val = field.get_ipap_field_value_string(value_encoded)
        record.insert_field(int(field_def['eno']), int(field_def['ftype']), field_val)

    def insert_integer_field(self, field_name: str, value: int, record: IpapDataRecord):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))

        if field.get_length() == 1:
            record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                                field.get_ipap_field_value_uint8(value))
        elif field.get_length() == 2:
            record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                                field.get_ipap_field_value_uint16(value))
        elif field.get_length() == 4:
            record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                                field.get_ipap_field_value_uint32(value))
        elif field.get_length() == 8:
            record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                                field.get_ipap_field_value_uint64(value))

    def insert_float_field(self, field_name: str, value: float, record: IpapDataRecord):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))
        record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                            field.get_ipap_field_value_float(value))

    def insert_double_field(self, field_name: str, value: float, record: IpapDataRecord):
        """
        Inserts a field value (double) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))
        record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                            field.get_ipap_field_value_double(value))

    def insert_ipv4_field(self, field_name: str, value: str, record: IpapDataRecord):
        """
        Inserts a field value (ip address 4) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(int(field_def['eno']), int(field_def['ftype']))
        value_encoded = value.encode('ascii')
        record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                            field.get_ipap_field_value_ipv4(value_encoded))

    def insert_ipv6_field(self, field_name: str, value: str, record: IpapDataRecord):
        """
        Inserts a field value (ip address 6) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(int(field_def['eno']), int(field_def['ftype']))
        value_encoded = value.encode('ascii')
        record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                            field.get_ipap_field_value_ipv6(value_encoded))

    def insert_datetime_field(self, field_name: str, value: datetime, record: IpapDataRecord):
        """
        Inserts a field value (datetime) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        seconds = int((value - datetime.fromtimestamp(0)).total_seconds())
        self.insert_integer_field(field_name, seconds, record)
