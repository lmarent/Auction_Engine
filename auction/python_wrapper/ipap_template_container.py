from ctypes import cdll
from ctypes import c_uint16
from python_wrapper.ipap_template import IpapTemplate
from foundation.singleton import Singleton
lib = cdll.LoadLibrary('libipap.so')

class IpapTemplateContainer(metaclass=Singleton):

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
        return lib.ipap_template_container_get_num_templates(self.obj)

    def __del__(self):
        lib.ipap_template_container_destroy(self.obj)

    def get_template(self, templid: int) -> IpapTemplate:
        obj = lib.ipap_template_container_get_template(self.obj, c_uint16(templid))
        if obj:  # not null
            ipap_template = IpapTemplate(obj=obj)
            return ipap_template
        else:
            raise ValueError('Template {0} not found'.format(str(templid)))
