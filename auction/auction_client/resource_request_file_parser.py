from lxml import etree
from lxml.etree import Element
from foundation.config import Config
from foundation.config_param import ConfigParam
from foundation.interval import Interval
from foundation.field_value import FieldValue

import pathlib
import os
from datetime import datetime
from auction_client.resource_request import ResourceRequest


class ResourceRequestFileParser:

    def __init__(self, domain: int):
        self.domain = domain

    @staticmethod
    def _convert_interal_dict(misc_config: dict) -> dict:
        """
        Converts the preference given to the required interval dictionary
        :param misc_config: set of preferences
        :return:
        """
        interval_dict = {}
        for key in misc_config:
            if key in ["start", "stop", "duration", "interval", "align"]:
                interval_dict[key] = misc_config[key].get_value()

        return interval_dict

    def _parse_interval(self, node: Element, start_at_least: datetime) -> (datetime, Interval):
        """
        Parses an interval
        :param node: xml node
        :param start_at_least:start datetime
        :return: start date time for the interval and interval parsed.
        """
        misc_config = {}
        for subitem in node.iterchildren():
            if isinstance(subitem.tag, str):
                if subitem.tag.lower() == "pref":
                    config_param = ConfigParam()
                    config_param.parse_config_item(subitem)
                    misc_config[config_param.name] = config_param

        interval_dict = self._convert_interal_dict(misc_config)

        new_interval = Interval()
        new_interval.parse_interval(interval_dict, start_at_least)
        return new_interval.stop, new_interval

    def _parse_resource_request(self, node: Element, global_set: str, time_format: str):
        """
        Parses an auction node in the xml.

        :param node: Element  element to parse
        :param global_set: str global set
        :return:
        """
        # get the Id property
        name = node.get("ID").lower()
        if global_set:
            set_name = global_set
        else:
            set_name = str(self.domain)

        resource_request_key = set_name + '.' + name
        resource_request = ResourceRequest(resource_request_key, time_format)

        # Iterates over children nodes
        start = datetime.now()
        for subitem in node.iterchildren():
            if isinstance(subitem.tag, str):
                if subitem.tag.lower() == "field":
                    field_value = FieldValue()
                    field_value.parse_field_value_from_xml(subitem)
                    resource_request.add_field_value(field_value)

                elif subitem.tag.lower() == "interval":
                    start, interval = self._parse_interval(subitem, start)
                    resource_request.add_interval(interval)

        return resource_request

    def parse(self, file_name: str) -> list:
        """
        parse resource request within the file given as parameter
        :param file_name file name including the absolute path of te file to parse.

        :return: list of resource request in the file
        """
        config = Config().get_config()

        if 'Main' not in config:
            raise ValueError("The main section was not defined in configuration option file")

        if 'ResourceRequestFileDtd' in config['Main']:
            the_dtd = config['Main']['ResourceRequestFileDtd']
        else:
            raise ValueError("The DTD ({}) configuration option does not exist!".format('ResourceRequestFileDtd'))

        base_dir = pathlib.Path(__file__).parent.parent
        the_dtd = base_dir / 'xmls' / the_dtd

        if not os.path.exists(the_dtd):
            raise ValueError("The DTD ({}) does not exist!".format(the_dtd))

        if 'TimeFormat' in config['Main']:
            time_format = config['Main']['TimeFormat']
        else:
            raise ValueError("The time format configuration option fos not exist")

        with open(the_dtd) as dtd_file:
            dtd = etree.DTD(dtd_file)
            tree = etree.parse(file_name)
            valid = dtd.validate(tree)

            if not valid:
                raise ValueError("XML given is invalid!")

            root = tree.getroot()
            g_set = root.get('ID').lower()

            resource_requests = []
            for item in root.iterchildren():
                if isinstance(item.tag, str):  # Only it takes xml nodes (remove comments).
                    if item.tag.lower() == "resource_request":
                        resource_request = self._parse_resource_request(item, g_set, time_format)
                        resource_requests.append(resource_request)

            return resource_requests
