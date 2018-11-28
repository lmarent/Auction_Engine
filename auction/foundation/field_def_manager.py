#field_def_manager.py 
import pathlib
import yaml
from foundation.singleton import Singleton
from enum import Enum


class DataType(Enum):
    """
    Datatypes being used for fields.
    """
    INVALID = -1
    EXPORTEND = 0
    LIST = 2
    LISTEND = 3
    CHAR = 4
    INT8 = 5
    INT16 = 6
    INT32 = 7
    INT64 = 8
    UINT8 = 9
    UINT16 = 10
    UINT32 = 11
    UINT64 = 12
    STRING = 13
    BINARY = 14
    IPV4ADDR = 15
    IPV6ADDR = 16
    FLOAT = 17
    DOUBLE = 18


class FieldDefManager(metaclass=Singleton):

    """
    Maintain field definitions and value definitions
    """
    def __init__(self, field_name_file=None, field_value_file=None):
        """
        Constructor for the class. It loads the field  and values definition files.

        :param field_name_file file to open and read with teh field definitions
        :param field_value_file file to open and read with values defined.
        """
        self.field_name_file = field_name_file
        self.field_value_file = field_value_file
        self.field_definitions = None
        self.field_values = None

        # Valid types are stored in lower cae
        self.valid_types = {
            'export_end' :DataType.EXPORTEND, 'list' : DataType.LIST,
            'listend' : DataType.LISTEND, 'char' : DataType.CHAR, 'int8' : DataType.INT8,
            'int16': DataType.INT16, 'int32' : DataType.INT32, 'int64' : DataType.INT64,
            'uint8' : DataType.UINT8, 'uint16' : DataType.UINT16, 'uint32' : DataType.UINT32,
            'uint64': DataType.UINT64, 'string' : DataType.STRING,
            'binary': DataType.BINARY, 'IpAddr' : DataType.IPV4ADDR,
            'Ip6Addr' : DataType.IPV6ADDR, 'float' :DataType.FLOAT,
            'double' : DataType.DOUBLE
            }
        self.valid_lengths = {
             DataType.CHAR : 1 ,  DataType.INT8 : 1,
             DataType.INT16 : 2,  DataType.INT32 : 4,  DataType.INT64 : 8,
             DataType.UINT8 : 1, DataType.UINT16 : 2, DataType.UINT32 : 4,
             DataType.UINT64 : 8, DataType.BINARY : 1, DataType.FLOAT : 4 ,
             DataType.DOUBLE : 8
            }

    def parse_field_type(self, field_type : str) -> DataType:

        if field_type.lower() in self.valid_types:
            return self.valid_types[field_type.lower()]
        else:
            raise ValueError("The field type given {0} is not a valid type".format(field_type))

    @staticmethod
    def _check_complete(self, field_definition):
        """

        :param field_definition: field definition to check
        :except ValueError : the field definition is not complete
        """
        if 'Type' not in field_definition:
            raise ValueError("The type was not provided for field")

        if 'Eno' not in field_definition:
            raise ValueError("The enterprise number was not provided for field")

        if 'Ftype' not in field_definition:
            raise ValueError("The field number was not provided for field")

        if 'Name' not in field_definition:
            raise ValueError("The name was not provided for field")

    def _check_field_length(self, field_type: DataType, field_length : int) -> int:
        """
        Checks the length and the type of field.
        :param field_type: field type (enumeration)
        :param field_length: lenght in bytes.
        :return: length in bytes to assign.
        """
        if field_type in self.valid_types:
            if self.valid_types[field_type] != field_length:
                raise ValueError("The field lenght {0} is not valid \
                                 for the type:{1}".format(str(field_length), str(DataType))
                                 )
            else:
                return self.valid_types[field_type]
        else:
            # 0 means varying length.
            return 0

    def _insert_field_defs(self, field_definitions):
        """
        Checks that field definitions are defined with the required structure
        """
        for key in field_definitions:
            try:
                # check a complete definition
                self._check_complete(field_definitions[key])

                # Check data type
                data_type = self.parse_field_type(self.field_definitions['Type'])

                # Check type and length consistency
                length = self._check_field_length(data_type, field_definitions[key]['Length'])

                # Insert the field definition
                self.field_definitions[key] = field_definitions[key]
                self.field.definitions[key]['type'] = data_type
                self.field.definitions[key]['eno'] = field_definitions[key]['Eno']
                self.field.definitions[key]['ftype'] = field_definitions[key]['Ftype']
                self.field.definitions[key]['name'] = field_definitions[key]['Name']
                self.field.definitions[key]['lenght'] = length

            except ValueError as e:
                print("field {0} not included - error: {1}".format(key, str(e)))

    def _check_field_values(self) -> bool:
        """
        Checks that field values are defined with the required structure
        """
        for field in self.field_values:
            #TODO: Checks whether the field exist as a field definition or not

            #TODO: Checks whether the type is as the one defined in the field definition.

            pass
        return True

    def _load_field_definitions(self, field_name_file=None):
        """
        Loads the field definition file. If not given as parameter, 
        it reads the default file definition to be found in the config folder.

        The file should be a yaml file with the following structure:
        field_def: 
           quantity:  --> identifier of the field
              Length: 8  --> length in bytes, optional for type string. 
              Type: Double  --> Type of the field valid values are: 
                    
                    Uint8|SInt8|UInt16|SInt16|UInt32|SInt32|UInt64|
                    SInt64|Bool|Binary|String|Float|Double|IPAddr|IP6Addr

              Eno: 0 
              Ftype: 33 --> id of te field to be used in templates.
              Name: Quantity --> Name of the field

        :param field_name_file file to open and read with the field definitions

        """ 
        if not field_name_file:
            # use the default file for field definitions
            base_dir = pathlib.Path(__file__).parent.parent
            field_name_file = base_dir / 'config' / 'field_definitions.yaml'
        
        with open(field_name_file) as f:
            field_defs = yaml.load(f)
            field_definitions = field_defs['field_def']

        self._insert_field_defs(field_definitions)

    def _load_field_values(self, field_value_file=None):
        """
        Loads field values files. if not given as parameter, it reads the
        field value file to be found in the config folder.

        The file should be a yaml file with the following structure:
        field_values:
            fieldname:
              Type: Double  --> Type of the field valid values are: 
                    
                    Uint8|SInt8|UInt16|SInt16|UInt32|SInt32|UInt64|
                    SInt64|Bool|Binary|String|Float|Double|IPAddr|IP6Addr
              
              Value: value to be assigned to the field.                 

        :param field_value_file file to open and read with values defined.

        """
        if not field_value_file:
            # use the default file for field definitions
            base_dir = pathlib.Path(__file__).parent.parent
            field_value_file = base_dir / 'config' / 'field_values.yaml'
        
        with open(field_value_file) as f:
            field_values = yaml.load(f)
            self.field_values = field_values['field_vals']

        self._check_field_values()

    def get_field_defs(self) -> dict:
        """
        Gets all field definitions
        :return:
        """
        if self.field_definitions is None:
            self._load_field_definitions(self.field_name_file)

        return self.field_definitions

    def get_field_vals(self)-> dict:
        """
        Gets all field values
        :return:
        """
        if self.field_values is None:
            self._load_field_values(self.field_value_file)

        return self.field_values

    def get_field(self, name: str) -> dict:
        """
        Gets a particular field from the dictionary of fields.
        :param name: name to get
        :return:
        """
        if self.field_definitions is None:
            self._load_field_definitions(self.field_name_file)

        if name in self.field_definitions:
            return self.field_definitions[name]
        else:
            raise ValueError("The field name {0} is not found in the field definition".format(name))

    def get_field_by_code(self, eno: int, ftype: int):
        """
        Finds a field within fiel definitions by eno and ftype.
        :param eno: enterprise no
        :param ftype: field number
        :return: field dictionary representing the field.
        """
        if self.field_definitions is None:
            self._load_field_definitions(self.field_name_file)

        for name in self.field_definitions:
            if self.field_definitions[name]['Eno'] == eno \
                    and self.field_definitions[name]['Ftype'] == ftype:
                return self.field_definitions[name]

        # Field not found
        raise ValueError("The field with eno:{0} ftype:{1} was not \
                         found in the field definition".format(str(eno), str(ftype)))

    def get_field_value(self, field_type: str, value: str) -> str:
        """
        Gets a articular field value by name
        :param field_type: field type of the value to get
        :param value: field value name.
        :return: field value
        """
        # Loads the field values if not did it before
        if self.field_values is None:
            self._load_field_values(self.field_value_file)

        if value in self.field_values:
            if self.field_values[value]['Type'] == field_type:
                return self.field_values[value]['Value']

        # Value not found
        raise ValueError("The field value with field type:{0} and value:{1} was not \
                         found in the field value definition".format(str(field_type), str(value)))
