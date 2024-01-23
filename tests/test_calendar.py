import unittest
from calendarLogic import CalendarLogic

class TestGregorianCalendar(unittest.TestCase):
    def test_convert_month_to_number(self):
        month = CalendarLogic.convert_month_to_number("March")
        self.assertEqual(month, 3)    

    def test_decrement_month(self):
        month, year = CalendarLogic.previous_month_and_year(2024, 1)
        self.assertEqual(month, 12)
        self.assertEqual(year, 2023)

    def test_increment_month(self):
        month, year = CalendarLogic.next_month_and_year(2023, 12)
        self.assertEqual(month, 1)
        self.assertEqual(year, 2024)

if __name__ == '__main__':
    unittest.main()
