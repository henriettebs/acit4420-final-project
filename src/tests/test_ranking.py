import unittest
from datetime import date, time
from types import SimpleNamespace
from unittest.mock import MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bus_bidder.ranking import (
    rank_relevant_offers,
    scoring_model,
    weighted_time,
    weighted_flexibility,
    calculate_uniform_distance,
    lower_is_better,
    get_cheapest_route
)

def make_offer(price=10, duration=100, transfers=0, dep_time=time(9,0), travel_date=date(2026,11,29), refundability=1, changeability=1):
    """Minimal fake offer with only the attributes the ranking code reads."""
    return SimpleNamespace(
        price=price,
        journey=SimpleNamespace(duration=duration, transfers=transfers),
        departure_time=dep_time,
        travel_date=travel_date,
        refundability=refundability,
        changeability=changeability,
        set_ranking=MagicMock(),
    )

def make_bid(dep_date=date(2026,11,29), dep_time="Any"):
    return SimpleNamespace(departure_date=dep_date, departure_time=dep_time)

class TestLowerIsBetter(unittest.TestCase):
    def test_lowest_value_scores_one(self):
        self.assertEqual(lower_is_better(10, 10, 30), 1.0)
    
    def test_highest_value_scores_zero(self):
        self.assertEqual(lower_is_better(30, 10, 30), 0.0)

    def test_middle_value(self):
        self.assertEqual(lower_is_better(20, 10, 30), 0.5)

    def test_all_equal_avoids_division_by_zero(self):
        self.assertEqual(lower_is_better(10, 10, 10), 1.0)

class TestUniformDistance(unittest.TestCase):
    def test_inside_range(self):
        self.assertEqual(calculate_uniform_distance(8, 6, 12), 1.0)
    
    def test_on_boundary(self):
        self.assertEqual(calculate_uniform_distance(6, 6, 12), 1.0)

    def test_outside_range_decreases(self):
        self.assertAlmostEqual(calculate_uniform_distance(4, 6, 12), (1 - 2 / 18)) # 2 hours before 6 (1 - distance / max_distance (= 18 hours))

    def test_never_negative(self):
        self.assertEqual(calculate_uniform_distance(0, 12, 18, max_dist=5), 0.0)

class TestWeightedTime(unittest.TestCase):
    def test_any_time_same_day(self):
        self.assertEqual(weighted_time(make_offer(), make_bid(dep_time="Any")), 1.0)

class TestFlexibility(unittest.TestCase):
    def test_fully_flexible(self):
        self.assertEqual(weighted_flexibility(make_offer(refundability=1, changeability=1)), 1.0)

    def test_refundable_counts_more(self):
        self.assertGreater(weighted_flexibility(make_offer(refundability=1, changeability=0)), weighted_flexibility(make_offer(refundability=0, changeability=1)))

    def test_inflexible(self):
        self.assertEqual(weighted_flexibility(make_offer(refundability=0, changeability=0)), 0.0)

class TestScoringModel(unittest.TestCase):
    def test_total_and_ranking_dict(self):
        weights = {"price": 0.4, "duration": 0.25, "transfers": 0.05, "time-convenience": 0.15, "flexibility": 0.15}
        offer = make_offer()

        score = scoring_model(weights, 1.0, 0.5, 0.0, 1.0, 1.0, offer)

        self.assertAlmostEqual(score, 0.825)
        offer.set_ranking.assert_called_once()
        ranking = offer.set_ranking.call_args[0][0]
        self.assertEqual(ranking["total_score"], "0.83")
        self.assertEqual(ranking["price_weight"], "0.40")

class TestRankOffers(unittest.TestCase):
    def setUp(self):
        self.bid = make_bid()
    
    def test_cheaper_offer_ranks_first_when_only_price_matter(self):
        weights = {"price": 1.0, "duration": 0, "transfers": 0, "time-convenience": 0, "flexibility": 0}
        cheap = make_offer(price=10)
        middle = make_offer(price=35)
        expensive = make_offer(price=50)

        result = rank_relevant_offers([middle, expensive, cheap], self.bid, weights)

        self.assertEqual(result, [cheap, middle, expensive])

    def test_fewer_transfers_win_when_only_transfers_matter(self):
        weights = {"price": 0, "duration": 0, "transfers": 1.0, "time-convenience": 0, "flexibility": 0}
        direct = make_offer(transfers=0)
        with_change = make_offer(transfers=1)
        with_many_changes = make_offer(transfers=3)
        
        result = rank_relevant_offers([with_change, direct, with_many_changes], self.bid, weights)

        self.assertEqual(result, [direct, with_change, with_many_changes])


class TestBestRoutes(unittest.TestCase):
    def test_cheapest_route(self):
        a, b = make_offer(price=30), make_offer(price=20)
        self.assertIs(get_cheapest_route([a,b]), b)


if __name__ == "__main__":
    unittest.main()