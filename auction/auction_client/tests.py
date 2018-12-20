import unittest
from auction_client.resource_request_file_parser import ResourceRequestFileParser



class ResourceRequestXmlFileParserTest(unittest.TestCase):

    def setUp(self):
        self.resource_request_file_parser = ResourceRequestFileParser(10)

    def test_parse(self):
        lst_resource_requests = self.resource_request_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_resource_request1.xml")

        self.assertEqual(len(lst_resource_requests), 1)
        resource_request = lst_resource_requests[0]

        # verifies the number of intervals
        self.assertEqual(len(resource_request.get_intervals()), 2)
