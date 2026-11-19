import unittest
from datetime import date, time, timedelta
from types import SimpleNamespace
from unittest.mock import patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bus_bidder.filtering import (
    filter_relevant_offers, 
    filter_offers_by_date,
    filter_offers_by_departure_time,
    filter_offers_by_checkbox,
    filter_offers_by_budget,
    filter_offers_by_customer_rating,
    filter_offers_by_transfers, 
    within_time_range
)

DAY = date(2026,11,29)

def make_offer(destination="Bilbao", travel_date=DAY, price=20.0, transfers=1,
               changeability=True, refundability=True, rating=4.0):
    return SimpleNamespace(
        journey=SimpleNamespace(destination_name=destination,
                                travel_date=travel_date,
                                transfers=transfers),
        price=price,
        changeability=changeability,
        refundability=refundability,
        customer_rating=rating,
    )


def make_bid(arrival_city="Bilbao", departure_date=DAY, budget=None,
             max_transfers=None, changeable=0, refundable=0,
             min_customer_rating=0.0):
    return SimpleNamespace(arrival_city=arrival_city,
                           departure_date=departure_date,
                           budget=budget,
                           max_transfers=max_transfers,
                           changeable=changeable,
                           refundable=refundable,
                           min_customer_rating=min_customer_rating)


class TestFilterByDate(unittest.TestCase):
    def test_same_day(self):
        self.assertTrue(filter_offers_by_date(DAY, DAY))
    
    def test_next_day(self):
        self.assertTrue(filter_offers_by_date(DAY, DAY + timedelta(days=1)))
    
    def test_two_days_later(self):
        self.assertFalse(filter_offers_by_date(DAY, DAY + timedelta(days=2)))
    
    def test_day_before(self):
        self.assertFalse(filter_offers_by_date(DAY, DAY - timedelta(days=1)))

class TestWithinTimeRange(unittest.TestCase):
    def test_inside(self):
        self.assertTrue(within_time_range(time(6), time(12), time(9)))
    
    def test_boundaries_are_inclusive(self):
        self.assertTrue(within_time_range(time(6), time(12), time(6)))
        self.assertTrue(within_time_range(time(6), time(12), time(12)))

    def test_outside(self):
        self.assertFalse(within_time_range(time(6), time(12), time(14)))

    def test_wrap_around_midnight(self):
        self.assertTrue(within_time_range(time(22), time(2), time(1)))

class TestFilterByDepartureTime(unittest.TestCase):
    def test_morning(self):
        self.assertTrue(filter_offers_by_departure_time("Morning (6-12)", time(9)))
        self.assertFalse(filter_offers_by_departure_time("Morning (6-12)", time(14)))

    def test_evening(self):
        self.assertTrue(filter_offers_by_departure_time("Evening (18-24)", time(23, 59)))
        self.assertFalse(filter_offers_by_departure_time("Evening (18-24)", time(17, 59)))
    
    def test_any__accepts_late_night_times(self):
        self.assertTrue(filter_offers_by_departure_time("Any", time(23, 30)))
    
class TestFilterByBudget(unittest.TestCase):
    def test_no_budget_accepts_everything(self):
        self.assertTrue(filter_offers_by_budget(None, 9999))
    
    def test_exactly_on_budget(self):
        self.assertTrue(filter_offers_by_budget(20.0, 20.0))

    def test_over_budget(self):
        self.assertFalse(filter_offers_by_budget(20.0, 20.1))

class TestFilterByTransfers(unittest.TestCase):
    def test_no_limit_values(self):
        for limit in (None, ""):
            with self.subTest(limit=limit):
                self.assertTrue(filter_offers_by_transfers(limit, 7))

    def test_over_limit(self):
        self.assertFalse(filter_offers_by_transfers(2, 4))

    def test_zero_means_direct_only(self):
        self.assertTrue(filter_offers_by_transfers(0, 0))
        self.assertFalse(filter_offers_by_transfers(0, 1))

class TestFilterByCheckbox(unittest.TestCase):
    def test_unchecked_accepts_everything(self):
        self.assertTrue(filter_offers_by_checkbox(0, True))
        self.assertTrue(filter_offers_by_checkbox(0, False))
    
    def test_checked_requires_true(self):
        self.assertTrue(filter_offers_by_checkbox(1, True))
        self.assertFalse(filter_offers_by_checkbox(1, False))

class TestFilterByRating(unittest.TestCase):
    def test_rating_filter(self):
        self.assertTrue(filter_offers_by_customer_rating(3.5, 4.2))
        self.assertFalse(filter_offers_by_customer_rating(3.5, 3.2))
        self.assertTrue(filter_offers_by_customer_rating(3.2, 3.2))
    
    def test_rating_is_converted(self):
        self.assertTrue(filter_offers_by_customer_rating(3.0, "3.9"))
    
class TestFilterRelevantOffers(unittest.TestCase):
    def test_matching_offer_is_kept(self):
        offer = make_offer()
        self.assertEqual(filter_relevant_offers([offer], make_bid()), [offer])

    def test_wrong_destination_removed(self):
        offer = make_offer(destination="Valencia")
        self.assertEqual(filter_relevant_offers([offer], make_bid()), [])
    
    def test_over_budget_removed(self):
        offer = make_offer(price=100)
        self.assertEqual(filter_relevant_offers([offer], make_bid(budget=50)), [])

    def test_not_changeable_removed_when_required(self):
        offer = make_offer(changeability=False)
        self.assertEqual(filter_relevant_offers([offer], make_bid(changeable=1)), [])

    def test_only_matching_offers_returned_in_order(self):
        good1 = make_offer(price=10)
        bad = make_offer(destination="Valencia")
        good2 = make_offer(price=30)
        result = filter_relevant_offers([good1, bad, good2], make_bid())
        self.assertEqual(result, [good1, good2])
    
    def test_all_filters_combined(self):
        bid = make_bid(budget=50, max_transfers=2, changeable=1, refundable=1,
                       min_customer_rating=3.0)
        offer = make_offer(price=49, transfers=2, rating=3.0)
        self.assertEqual(filter_relevant_offers([offer], bid), [offer])

        
if __name__ == "__main__":
    unittest.main()