from lxml import etree
from lxml.etree import Element

from foundation.config import Config
from foundation.ipap_message_parser import IpapMessageParser
from foundation.bidding_object import BiddingObject
from foundation.config_param import ConfigParam

import pathlib
import os
from typing import List


class BiddingObjectXmlFileParser(IpapMessageParser):
    """
    This class parses files containing bidding ojects.


    A configuration item is a tuple of three values:
        name : name of the configuration item
        type : type of the configuration item
        value: value in string.

    """

    def __init__(self, domain: int):
        super(BiddingObjectXmlFileParser, self).__init__(domain=domain)

    @staticmethod
    def _parse_element(item: Element) -> dict:
        """
        Parses an element within the bidding object

        :param item: xml item to parse.
        :return: dictionary with the element parsed.
        """
        element_fields = {}
        for sub_item in item.iterchildren():
            if isinstance(sub_item.tag, str):
                if sub_item.tag.lower() == "field":
                    config_param = ConfigParam()
                    config_param.parse_config_item(sub_item)
                    element_fields[config_param.name] = config_param

        return element_fields

    @staticmethod
    def _parse_option(item: Element) -> dict:
        """
        Parses an option within the bidding object

        :param item: xml item to parse.
        :return: dictionary with the options parsed.
        """
        option_fields = {}
        for sub_item in item.iterchildren():
            if isinstance(sub_item.tag, str):
                if sub_item.tag.lower() == "pref":
                    config_param = ConfigParam()
                    config_param.parse_config_item(sub_item)
                    option_fields[config_param.name] = config_param

        return option_fields

    def _parse_bidding_object(self, item: Element) -> BiddingObject:
        """
        Parses a bidding object within the xml

        :param item: item to parse
        :return: bidding object
        """
        # get the auction key
        auction_key = item.get("AUCTION_ID").lower()

        # get bidding object's type
        stype = item.get("TYPE").lower()
        bidding_object_type = self.parse_type(stype)

        # Get Bidding object Id
        bidding_object_key = item.get("ID").lower()

        # Get elements and options.
        elements = {}
        options = {}
        # Iterates over children nodes
        for subitem in item.iterchildren():
            if isinstance(subitem.tag, str):
                if subitem.tag.lower() == "element":
                    element_id = subitem.get("ID")
                    element = self._parse_element(subitem)
                    elements[element_id] = element

                elif subitem.tag.lower() == "option":
                    option_id = subitem.get("ID")
                    option = self._parse_option(subitem)
                    options[option_id] = option

        bidding_object_type = self.get_auctioning_object_type(bidding_object_type)
        bidding_object = BiddingObject(auction_key, bidding_object_key, bidding_object_type, elements, options)
        return bidding_object

    def parse(self, file_name: str) -> List[BiddingObject]:
        """
        parses the bidding objects within the file

        :param file_name: file name to parse
        :return: list of bidding objects parsed.
        """
        the_dtd = Config().get_config_param('Main', 'BiddingObjectfileDtd')
        base_dir = pathlib.Path(__file__).parent.parent
        the_dtd = base_dir / 'xmls' / the_dtd

        if not os.path.exists(the_dtd):
            raise ValueError("The DTD ({}) does not exist!".format(the_dtd))

        bidding_objects = []
        with open(the_dtd) as dtd_file:
            dtd = etree.DTD(dtd_file)
            tree = etree.parse(file_name)
            valid = dtd.validate(tree)

            if not valid:
                raise ValueError("XML given is invalid!")

            root = tree.getroot()

            for item in root.iterchildren():
                if isinstance(item.tag, str):  # Only it takes xml nodes (remove comments).
                    if item.tag.lower() == "bidding_object":
                        bidding_object = self._parse_bidding_object(item)
                        bidding_objects.append(bidding_object)

        return bidding_objects
