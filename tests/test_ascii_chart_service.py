# test_ascii_chart_service.py
import unittest
from service.ascii_chart_service import format_table, adjust_spacing


class TestAsciiChartService(unittest.TestCase):

    def test_format_table_with_valid_data(self):
        data = [
            {'display_name': 'user1', 'yo_count': 200},
            {'display_name': 'user2', 'yo_count': 100},
            {'display_name': 'user3', 'yo_count': 50},
            {'display_name': 'user4', 'yo_count': 0},
        ]
        result = format_table(data)
        self.assertIn('user1', result)
        self.assertIn('user2', result)
        self.assertIn('user3', result)
        self.assertIn('user4', result)

    def test_format_table_with_empty_data(self):
        data = []
        result = format_table(data)
        self.assertEqual('', result)

    def test_format_table_with_exception(self):
        data = [
            {'display_name': 'user1', 'yo_count': 200},
            # This will cause an exception
            {'display_name': 'user2', 'yo_count': 'invalid'},
        ]
        result = format_table(data)
        self.assertIn('user1', result)
        self.assertIn('user2', result)

    def test_adjust_spacing(self):
        input_data = [('user1', 200), ('user2', 100), ('user3', 50)]
        expected_output = [('user1', 200), ('user2', 100), ('user3', 50)]
        result = adjust_spacing(input_data)
        self.assertEqual(result, expected_output)

    def test_adjust_spacing_with_different_lengths(self):
        input_data = [('u1', 200), ('user2', 100), ('u3', 50)]
        expected_output = [('u1   ', 200), ('user2', 100), ('u3   ', 50)]
        result = adjust_spacing(input_data)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
