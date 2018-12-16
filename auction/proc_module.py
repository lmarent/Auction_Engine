from foundation.module import Module
from foundation.config import Config

info_labels = ['name', 'id','version','created', 'modified', 'brief', 'verbose', 'htmldoc', 'parameters',
               'results', 'name', 'affiliation', 'email', 'homepage'
              ]


class ProcModule(Module):
    """
    Container class that stores information about an evaluation module

    Container class - stores information about an evaluation module, such as
    name, uid, function list, module_handle and reference counter.
    """
    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        """
        constructor for the class
        :param module_name: module name
        :param module_file: module file
        :param module_handle: module handle
        :param config_group:
        """
        super(ProcModule,self).__init__(module_name, module_file,module_name, module_handle)
        self.config_group = config_group
        self.active_timers = 0
        self.config = Config().get_config()
        self.config_param_list = Config().get_items(self.config_group, module_name)
        self.init_module(self.config_param_list)
