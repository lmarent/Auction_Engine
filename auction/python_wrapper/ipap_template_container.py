from ctypes import cdll
from ctypes import c_uint16
from python_wrapper.ipap_template import IpapTemplate
lib = cdll.LoadLibrary('libipap.so')

class IpapTemplateContainer:

    def __init__(self):
        self.obj = lib.ipap_template_container_new()

    def add_template(self, template : IpapTemplate):
        lib.ipap_template_container_add_template(self.obj, template.obj)

    def delete_all_templates(self):
        lib.ipap_template_container_delete_all_templates(self.obj)

    def delete_template(self, templid : int):
        lib.ipap_template_container_delete_template(self.obj, c_uint16(templid))

    def exists_template(self, templid : int):
        return lib.ipap_template_container_exists_template(self.obj, c_uint16(templid))

    def get_num_templates(self) -> int:
        return lib.ipap_template_container_get_num_templates()