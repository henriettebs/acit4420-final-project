from datetime import time, timedelta

def filter_relevant_offers(offers, bid):
    """Filter offers based on the bid criteria."""    
    filtered_offers = []
    for offer in offers:
        destination_match = offer.journey.destination_name == bid.arrival_city
        correct_date = filter_offers_by_date(bid.departure_date, offer.journey.travel_date)
        #in_time_range = filter_offers_by_departure_time(bid.departure_time, offer.journey.departure_time)
        in_budget = filter_offers_by_budget(bid.budget, offer.price)
        below_max_transfers = filter_offers_by_transfers(bid.max_transfers, offer.journey.transfers)
        is_changeable = filter_offers_by_checkbox(bid.changeable, offer.changeability)
        is_refundable = filter_offers_by_checkbox(bid.refundable, offer.refundability)
        above_min_rating = filter_offers_by_customer_rating(bid.min_customer_rating, offer.customer_rating)

        if (destination_match and
            correct_date and
            #in_time_range and
            in_budget and
            below_max_transfers and
            is_changeable and
            is_refundable and
            above_min_rating):
            filtered_offers.append(offer)

    return filtered_offers

def filter_offers_by_date(departure_date, offer_travel_date):
    """Filter offers based on the departure date."""
    return departure_date == offer_travel_date or (departure_date + timedelta(days=1)) == offer_travel_date

def filter_offers_by_departure_time(departure_time, offer_departure_time):
    """Filter offers based on the departure time."""
    t1 = time(00)
    t2 = time(23)
    ot = offer_departure_time
    match departure_time:
        case "Morning (6-12)":
            t1 = time(6)
            t2 = time(12)
            return within_time_range(t1, t2, ot)
        case "Afternoon (12-18)":
            t1 = time(12)
            t2 = time(18)
            return within_time_range(t1, t2, ot)
        case "Evening (18-24)":
            t1 = time(18)
            t2 = time(00)
            return within_time_range(t1, t2, ot)
        case "Night (0-6)":
            t1 = time(00)
            t2 = time(6)
            return within_time_range(t1, t2, ot)
        case "Any":
            return True
    return within_time_range(t1, t2, ot)

def within_time_range(t1, t2, ot):
    """Check if the offer time is within the specified time range."""
    if t2 < t1:  # Handle the case where the time range wraps around midnight
        return ot >= t1 or ot <= t2
    return t1 <= ot <= t2

def filter_offers_by_budget(budget, offer_price):
    """Filter offers based on the budget."""
    if budget is None or budget == 0.0:
        return True  # If no budget is specified, all offers are valid
    return offer_price <= budget

def filter_offers_by_transfers(max_transfers, offer_transfers):
    """Filter offers based on the maximum number of transfers."""
    if max_transfers is None or max_transfers == "" or max_transfers == 100:
        return True  # If no maximum transfers are specified, all offers are valid
    return offer_transfers <= max_transfers

def filter_offers_by_checkbox(bid_checkbox, offer_boolean):
    """Filter offers based on the changeable and refundable checkboxes."""
    if bid_checkbox == 0:
        return True  # If no preference is specified, all offers are valid
    elif bid_checkbox == 1 and offer_boolean:
        return True  # If changeable is specified and the offer is changeable, it's valid
    return False  # If none of the above conditions are met, the offer is not valid

def filter_offers_by_customer_rating(min_rating, offer_rating):
    """Filter offers based on the minimum customer rating."""
    try:
        offer_rating = float(offer_rating)
    except ValueError:
        print(f"Invalid offer rating: {offer_rating}. Skipping this offer.")
        return False  # If the offer rating is not a valid float, skip this offer
    return offer_rating >= min_rating