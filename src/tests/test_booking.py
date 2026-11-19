import unittest
import uuid
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import BusBidderApp

class TestBooking(unittest.TestCase):
    correct_booking = {
        "booking_reference": f"0B{uuid.uuid4().hex[:8].upper()}",
        "traveller_name": "George Leavitt",
        "traveller_email": "gele@gmail.com",
        "traveller_phone": "004792334151",
        "offer_id": "0F0541",
        "company": "SolRuta",
        "departure_city": "Madrid",
        "arrival_city": "Bilbao",
        "departure_date": "2026-11-29",
        "departure_time": "10:00",
        "arrival_date": "2026-11-29",
        "arrival_time": "17:57",
        "duration": "477",
        "transfers": "1",
        "environmental_measure": "Standard",
        "price": "21.12",
        "luggage_allowance": "20",
        "changeability": "True",
        "flexibility": "True",
        "available_seats": "19",
        "customer_rating": "3.9",
        "seats_booked":"2"
    }
    
    def setUp(self):
        self.app = MagicMock()
        self.app.name_entry.get.return_value = "George Leavitt"
        self.app.email_entry.get.return_value = "gele@gmail.com"
        self.app.phone_entry.get.return_value = "004792334151"
        self.app.booking_entry.get.return_value = 2
        
        self.offer = SimpleNamespace(
            offer_id = "0F0541",
            company = "SolRuta",
            available_seats = 19
        )
    
    @patch("main.write_booking")
    @patch("main.validate_confirmation_query", return_value=None)
    def test_successful_booking(self, mock_validate, mock_write):
        BusBidderApp.confirm_booking_click(self.app, self.offer)
        #Booking was saved exactly once, with the right data
        mock_write.assert_called_once()
        booking = mock_write.call_args[0][0]
        self.assertTrue(booking.booking_reference.startswith("0B"))
        self.assertEqual(len(booking.booking_reference), 10)
        self.assertEqual(booking.traveller.name, "George Leavitt")
        self.assertEqual(booking.traveller.email, "gele@gmail.com")

        #Confirmation window shown, error window not
        self.app.confirm_booking_window.assert_called_once_with(booking)
        self.app.open_error_window.assert_not_called()

    @patch("main.write_booking")
    @patch("main.validate_confirmation_query", return_value="Invalid email")
    def test_validation_error(self, mock_validate, mock_write):
        BusBidderApp.confirm_booking_click(self.app, self.offer)

        self.app.open_error_window.assert_called_once_with("Invalid email")
        mock_write.assert_not_called()
        self.app.confirm_booking_window.assert_not_called()
        
    @patch("main.write_booking")
    @patch("main.validate_confirmation_query", return_value=None)
    @patch("main.uuid")
    def test_booking_reference_format(self, mock_uuid, mock_validate, mock_write):
        mock_uuid.uuid4.return_value.hex = "abcdef1234567890"

        BusBidderApp.confirm_booking_click(self.app, self.offer)

        booking = mock_write.call_args[0][0]
        self.assertEqual(booking.booking_reference, "0BABCDEF12")

    @patch("main.write_booking")
    @patch("main.validate_confirmation_query", return_value=None)
    def test_validation_error_seats(self, mock_validate, mock_write):
        BusBidderApp.confirm_booking_click(self.app, self.offer)

        booking = mock_write.call_args[0][0]
        self.assertGreaterEqual(booking.seats_booked, 1)


if __name__ == "__main__":
    unittest.main()