import unittest
from unittest.mock import patch
from selenium.common.exceptions import NoSuchElementException

import backend.resources
from backend.selenium_app.order_sub_auto import OrderSubFunctionDiagnostic, order_sub
from backend.twilio_app.helpers import SubOrder
from datetime import datetime

class TestOrderSub(unittest.TestCase):

    def setUp(self) -> None:
        self.order = SubOrder(requested_sub="Boar's Head Italian",
                              store_name="St Pete Beach",
                              date_of_order=datetime.today().date().strftime("%A, %B %d, %Y"))
        self.diagnostic = OrderSubFunctionDiagnostic()

    def test_diagnostic_initialization(self):
        self.assertIsNone(self.diagnostic.selected_store_location)
        self.assertIsNone(self.diagnostic.selected_sandwich)
        self.assertIsNone(self.diagnostic.run_speed)
        self.assertIsNone(self.diagnostic.user_agent)
        self.assertIsNone(self.diagnostic.official_location_name)
        self.assertIsNone(self.diagnostic.sandwich_name)
        self.assertIsNone(self.diagnostic.pickup_time)
        self.assertIsNone(self.diagnostic.first_name)
        self.assertIsNone(self.diagnostic.last_name)
        self.assertIsNone(self.diagnostic.phone_number)
        self.assertIsNone(self.diagnostic.email)

    # @patch("backend.resources.create_webdriver")
    # def test_order_sub(self, mock_create_webdriver):
    #     mock_driver = mock_create_webdriver.return_value
    #
    #     with self.assertRaises(NoSuchElementException):
    #         order_sub(self.order, self.diagnostic)
    #
    #     self.assertEqual(self.diagnostic.selected_store_location, "St Pete Beach")
    #     self.assertEqual(self.diagnostic.selected_sandwich, "Boar's Head Italian")
    #     self.assertEqual(self.diagnostic.run_speed, "fast")
    #     self.assertEqual(self.diagnostic.user_agent, "chrome")
    #     self.assertEqual(self.diagnostic.official_location_name, "St Pete Beach")
    #     self.assertEqual(self.diagnostic.sandwich_name, "Boar's Head Italian")