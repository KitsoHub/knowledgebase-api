""" Sample tests"""
from django.test import SimpleTestCase
from app import sample_cal_test


class SampleCalTests(SimpleTestCase):
    """Calculation class"""

    def test_add_numbers(self):
        res = sample_cal_test.add(4,3)
        self.assertEqual(res, 7)

    def test_subtract_numbers(self):
        res = sample_cal_test.subtract(2, 1)
        self.assertEqual(res, 1)