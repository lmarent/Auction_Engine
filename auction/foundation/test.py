import unittest
from foundation.field_def_manager import FieldDefManager


class DefFileManagerTest(unittest.TestCase):

    def setUp(self):
        self.def_file_manager = FieldDefManager()

    def test_get_field_defs(self):
        field_defs = self.def_file_manager.get_field_defs()
        self.assertEqual(len(field_defs), 53)

    def test_get_field_vals(self):
        field_vals = self.def_file_manager.get_field_vals()
        self.assertEqual(len(field_vals), 1)

    def test_get_field(self):
        # Value found
        field_found = self.def_file_manager.get_field("templatelist")
        self.assertEqual(field_found['Type'], "String")

        # Value not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field("templatelist")

