import os
import importlib
import importlib.util

class ModuleLoader:

    def __init__(self, module_directory:str, modules: str, group: str ):
        self.group = group
        self.modules = {}

        if not module_directory:
            raise ValueError("ModuleLoader: invalid empty module directory")

        # adds '/' if dir does not end in one already
        if module_directory[len(module_directory)-1] != '/':
            module_directory += "/"

        # test if specified dir does exist
        if os.path.isdir(module_directory):
            raise ValueError("ModuleLoader: invalid module directory {0}".format(module_directory))

        self.module_directory = module_directory

        # loads modules included in the list. We expect the list separated by comma(,)
        if modules:
            names = modules.split(',')
            for name in names:
                self.load_module(name, True)

    def load_module(self, module_name: str, preload: bool) -> Module:
        """
        Loads a specific module
        :param module_name: module name to be loaded
        :param preload: if it is loaded at the start of the auctioner
        :return module loaded
        """
        if not module_name:
            raise ValueError("Invalid module name, it is empty")

        # the module name is relative
        if '/' not in module_name:
            file_name = self.module_directory + module_name

        # Check if the module can be imported
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        if spec is None:
            raise ModuleNotFoundError("The module with name {0} can not be open".format(file_name))

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        proc_module = ProcModule(module)
        self.modules[module_name] = proc_module
        return proc_module

    def get_module(self):

    def release_module(self, module: Module):


    def get_version(self, module_name: str):
