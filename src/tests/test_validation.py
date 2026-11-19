import unittest 
from datetime import date, timedelta
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bus_bidder.validation import (
    validate_search_query,
    validate_confirmation_query,
    validate_offer
)

FUTURE = date.today() + timedelta(days=10)
PAST = date.today() - timedelta(days=1)

class TestValidateSearchQuery(unittest.TestCase):
    def call(self, **overrides):
        args = dict(departure_date=FUTURE.isoformat(), budget="100", 
                    max_transfers="2", changeable=1, refundable=0,
                    min_customer_rating=3.5)
        args.update(overrides)
        return validate_search_query(**args)
    
    def test_valid_query_returns_none(self):
        self.assertIsNone(self.call())
    
    def test_empty_fields_are_optional(self):
        self.assertIsNone(self.call(budget="", max_transfers=""))

    def test_wrong_date_format(self):
        self.assertIn("Incorrect value", self.call(departure_date="2026/11/20"))
    
    def test_date_in_past(self):
        self.assertIn("Date is out of range", self.call(departure_date=PAST.isoformat()))
    
    def test_budget_not_a_number(self):
        self.assertIn("Budget", self.call(budget="fifty"))
    
    def test_negative_budget_rejected(self):
        self.assertIn("Budget", self.call(budget="-5"))
    
    def test_transfers_not_a_number(self):
        self.assertIn("Transfers", self.call(max_transfers="two"))

    def test_checkbox_invalid_value(self):
        self.assertIn("Incorrect type", self.call(changeable=2))
        self.assertIn("Incorrect type", self.call(refundable=5))

    def test_negative_rating(self):
        self.assertIn("rating", self.call(min_customer_rating=-1))

class TestValidateConfirmationQuery(unittest.TestCase):
    def call(self, **overrides):
        args = dict(booking_reference="0BABCDEF12", name="George Leavitt", 
                    email="gele@gmail.com", phone_number="004792334151",
                    seats="2", seats_available=18)
        args.update(overrides)
        return validate_confirmation_query(**args)
    
    def test_valid_booking_reference(self):
        self.assertIsNone(self.call())
    
    def test_booking_reference_missing(self):
        self.assertIn("identifier", self.call(booking_reference=None))

    def test_booking_reference_wrong_format(self):
        for ref in ("XX12345678", "0B123", "0BABCDEF123", "0b12345678"):
            with self.subTest(ref=ref):
                self.assertIn("identifier", self.call(booking_reference=ref))
    
    def test_empty_name(self):
        self.assertIn("Name cannot be empty", self.call(name=""))
    
    def test_name_with_digits(self):
        self.assertIn("Incorrect type", self.call(name="George123"))

    def test_invalid_emails(self):
        for email in ("not-an-email", "a@b", "@gmail.com"):
            with self.subTest(email=email):
                self.assertIn("Email must be", self.call(email=email))
    
    def test_invalid_phone_numbers(self):
        for phone in ("123", "abbbsere", "923452"):
            with self.subTest(phone=phone):
                self.assertIn("Phone number must be", self.call(phone_number=phone))
    
    def test_no_seats_entered(self):
        self.assertIn("Atleast one seat", self.call(seats=""))
    
    def test_more_seats_than_availble(self):
        self.assertIn("Out of range", self.call(seats="20"))
    
    def test_exactly_all_availble_seats_is_ok(self):
        self.assertIsNone(self.call(seats="18"))

    def test_zero_seats_as_string_rejected(self):
        self.assertIsNotNone(self.call(seats="0"))

    def test_negative_seats_rejected(self):
        self.assertIsNotNone(self.call(seats="-3"))

class TestValidateOffer(unittest.TestCase):
    def offer(self, **overrides):
        o = {
            "offer_id": "0F0541",
            "destination": "Bilbao",
            "travel_date": FUTURE.isoformat(),
            "arrival_date": FUTURE.isoformat(),
            "departure_time": "10:00",
            "price": "21.12",
            "duration": "477",
            "changeability": "True",
            "refundability": "False",
            "available_seats": "19",
            "customer_rating": "3.9",
        }
        o.update(overrides)
        return o

    def test_valid_offer_returns_none(self):
        self.assertIsNone(validate_offer(self.offer(), offer_ids=[]))

    def test_invalid_offer_id_format(self):
        for oid in ("0F012", "XX0541", "0F05412", "0f0541"):
            with self.subTest(oid=oid):
                result = validate_offer(self.offer(offer_id=oid), [])
                self.assertIn("identifier", result)

    def test_duplicate_offer_id(self):
        result = validate_offer(self.offer(), offer_ids=["0F0541"])
        self.assertIn("identifier", result)

    def test_travel_date_wrong_format(self):
        result = validate_offer(self.offer(travel_date="29-11-2026"), [])
        self.assertIn("YYYY-MM-DD", result)
    
    def test_arrival_before_departure(self):
        result = validate_offer(self.offer(arrival_date=PAST.isoformat()), [])
        self.assertIn("Arrival date", result)

    def test_invalid_departure_time(self):
        for t in ("25:00", "10:60", "9:00", "10-00"):
            with self.subTest(t=t):
                self.assertIn("HH:MM", validate_offer(self.offer(departure_time=t), []))

    def test_rating_out_of_range(self):
        for r in ("0", "5.1", "-1"):
            with self.subTest(r=r):
                self.assertIn("Out of range", validate_offer(self.offer(customer_rating=r), []))

if __name__ == "__main__":
    unittest.main()