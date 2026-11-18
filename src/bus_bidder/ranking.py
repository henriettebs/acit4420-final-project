from datetime import timedelta

def rank_relevant_offers(offers, bid, weights):
    """Rank offers based on price, journey duration, transfers, departure-time convenience and ticket flexibility."""
    prices = [o.price for o in offers]
    durations = [o.journey.duration for o in offers]
    transfers = [o.journey.transfers for o in offers]
    p_min, p_max = min(prices), max(prices)
    d_min, d_max = min(durations), max(durations)
    t_min, t_max = min(transfers), max(transfers)

    print(f"Weights: {weights}")
    def score(o):
        return scoring_model(weights, weighted_price(o.price, p_min, p_max), 
                      weighted_duration(o.journey.duration, d_min, d_max),
                      weighted_transfers(o.journey.transfers, t_min, t_max),
                      weighted_time(o, bid), 
                      weighted_flexibility(o),
                      o)

    return sorted(offers, key=score, reverse=True)

def scoring_model(weights, s_price, s_duration, s_transfers, s_time, s_flexibility, o):
    w_price = weights['price'] * s_price
    w_duration = weights['duration'] * s_duration
    w_transfers =  weights['transfers'] * s_transfers
    w_time = weights['time-convenience'] * s_time
    w_flexibility = weights['flexibility'] * s_flexibility

    score = w_price + w_duration + w_transfers + w_time +  w_flexibility
    ranking = {
        "total_score": f"{score:.2f}",
        "price_score": float(s_price),
        "duration_score": float(s_duration),
        "transfer_score": float(s_transfers),
        "time_score": float(s_time),
        "flex_score": float(s_flexibility),
        "price_weight": f"{w_price:.2f}",
        "duration_weight": f"{w_duration:.2f}",
        "transfer_weight": f"{w_transfers:.2f}",
        "time_weight": f"{w_time:.2f}",
        "flex_weight": f"{w_flexibility:.2f}"
    }
    o.set_ranking(ranking)
    #print(f"{score:.1f} = {w_price:.1f} + {w_duration:.1f} + {w_transfers:.1f} + {w_time:.1f} + {w_flexibility:.1f}")
    return score

def weighted_price(p, low, high):
    p, low, high = float(p), float(low), float(high)
    return lower_is_better(p, low, high)

def weighted_duration(d, low, high):
    d, low, high = float(d), float(low), float(high)
    return lower_is_better(d, low, high)

def weighted_transfers(t, low, high):
    t, low, high = int(t), int(low), int(high)
    return lower_is_better(t, low, high)

# Use uniform distance to check how far it is outside the range, and if in range return a high value (1.0)
def weighted_time(o, b):
    #print(f"Offer: {o.travel_date} {o.departure_time} and Bid: {b.departure_date} {b.departure_time}")
    t = o.departure_time.hour + o.departure_time.minute / 60

    if o.travel_date == b.departure_date:
        match b.departure_time:
            case "Any":
                return 1.0 # All departure times this day are a great fit = good ranking
            case "Morning (6-12)":
                return calculate_uniform_distance(t, 6, 12)
            case "Afternoon (12-18)":
                return calculate_uniform_distance(t, 12, 18)
            case "Evening (18-24)":
                return calculate_uniform_distance(t, 18, 24)
            case "Night (0-6)":
                return calculate_uniform_distance(t, 0, 6)
    elif o.travel_date == b.departure_date + timedelta(days=1): # The next day ranks lower than original departure date
        result = 0.5 * (1 - t / 24) # The further from the original departure date in hours and minutes, the lower the ranking
        return result
    else: # Any other day
        return 0.01
    
def calculate_uniform_distance(t, low, high, max_dist=18):
    if low <= t <= high:
        return 1.0 # Departure time within wanted time frame = good ranking
    dist = min(abs(t - low), abs(t - high))
    #print(f"1 - {dist}/{max_dist} = {1 - dist/max_dist}")
    return max(0.0, 1 - dist/max_dist)

def weighted_flexibility(o):
    return 0.6 * o.refundability + 0.4 * o.changeability # Better ranking for refundability, than changability, as it adds more value to the flexibility of the traveller

def lower_is_better(v, l, h):
    return 1.0 if l == h else (h - v) / (h - l)

"""Finding the cheapset, fastest, and best rated route as additional feedback to the traveller"""
def get_cheapest_route(offers):
    cheapest_route = min(offers, key=lambda o: o.price)
    return cheapest_route

def get_shortest_route(offers):
    fastest_route = min(offers, key=lambda o: o.duration)
    return fastest_route

def get_best_rated_route(offers):
    best_rated_route = max(offers, key=lambda o: o.customer_rating)
    return best_rated_route