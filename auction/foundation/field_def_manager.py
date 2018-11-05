#field_def_manager.py 
import pathlib
import yaml

class FieldDefManager():
    """
    Maintain field definitions and value definitions
    """
    def __init__(self, field_name_file=None, field_value_file=None):
        """
        Constructor for the class. It loads the field  and values definition files.

        :param field_name_file file to open and read with teh field definitions
        :param field_value_file file to open and read with values defined.
        """
        self.field_definitions = {}
        self.field_values = {}
        self._load_field_definitions(field_name_file)
        self._load_field_values(field_value_file)

    def _check_field_defs(self):
        """
        Checks that field definitions are defined with the required structure
        """
        for key in self.field_definitions:
            # TODO: check the field definition is complete 

            # TODO: check valid type 

            # TODO: Check type and lenght consistency
            pass

    def _check_field_values(self):
        """
        Checks that field values are defined with the required structure
        """
        for field in field_values:
            #TODO: Checks whether the field exist as a field definition or not

            #TODO: Checks whether the type is as the one defined in the field definitio.

            pass

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
            # use the default file for field definicions
            BASE_DIR = pathlib.Path(__file__).parent.parent
            field_name_file = BASE_DIR / 'config' / 'field_definitions.yaml'
        
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
            BASE_DIR = pathlib.Path(__file__).parent.parent
            field_value_file = BASE_DIR / 'config' / 'field_values.yaml'
        
        with open(field_value_file) as f:
            field_values = yaml.load(f)
            self.field_values = field_values['field_vals']

        self._check_field_vals()

