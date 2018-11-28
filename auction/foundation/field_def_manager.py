#field_def_manager.py 
import pathlib
import yaml
from foundation.singleton import Singleton


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

    def _check_field_defs(self) -> bool:
        """
        Checks that field definitions are defined with the required structure
        """
        for key in self.field_definitions:
            # TODO: check the field definition is complete 

            # TODO: check valid type 

            # TODO: Check type and length consistency
            pass
        return True

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
            self.field_definitions = field_defs['field_def']

        self._check_field_defs()

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
