from lxml import etree
from lxml.etree import Element
from foundation.config import Config

import pathlib
import os


class ResourceRequestFileParser:


    def __init__(self):
        pass

    def parse(self, file_name: str) -> list:
        """
        parse resource request within the file given as parameter
        :param file_name file name including the absolute path of te file to parse.

        :return: list of resource request in the file
        """
        config = Config().get_config()

        if 'ResourceRequestFileDtd' in config:
            the_dtd = config['ResourceRequestFileDtd']
        else:
            raise ValueError("The DTD ({}) configuration option does not exist!".format('ResourceRequestFileDtd'))

        if 'ResourceRequestRootNode' in config:
            root_node = config['ResourceRequestRootNode']
        else:
            raise ValueError("The DTD Root Node({}) configuration option does not exist!".format('ResourceRequestRootNode'))

        parser = etree.XMLParser(dtd_validation=True)
        base_dir = pathlib.Path(__file__).parent.parent
        the_dtd = base_dir / 'xmls' / the_dtd

        if not os.path.exists(the_dtd):
            raise ValueError("The DTD ({}) does not exist!".format(the_dtd))

        with open(the_dtd) as dtd_file:
            dtd = etree.DTD(dtd_file)
            tree = etree.parse(file_name)
            valid = dtd.validate(tree)

            if not valid:
                raise ValueError("XML given is invalid!")

            root = tree.getroot()
            g_set = root.get('ID').lower()

            ipap_field_container = IpapFieldContainer()
            ipap_field_container.initialize_reverse()
            ipap_field_container.initialize_forward()

            auctions = []
            for item in root.iterchildren():
                if isinstance(item.tag, str):  # Only it takes xml nodes (remove comments).
                    if item.tag.lower() == "global":
                        (global_misc_config, global_actions) = self._parse_global_options(item)
                    elif item.tag.lower() == "auction":
                        auction = self._parse_auction(item, g_set, global_misc_config,
                                                      global_actions, ipap_field_container
                                                      )
                        auctions.append(auction)

            return auctions
