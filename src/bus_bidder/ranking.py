def rank_relevant_offers(offers, bid, weights):
    """Rank offers based on price, journey duration, transfers, departure-time convenience and ticket flexibility."""
    prices = [o['price'] for o in offers]
    durations = [o['duration'] for o in offers]
    transfers = [o['transfers'] for o in offers]
    print(prices, durations)
    p_min, p_max = min(prices), max(prices)
    d_min, d_max = min(durations), max(durations)
    t_min, t_max = min(transfers), max(transfers)

    print(f"Prices: [{p_min}, {p_max}]\nDurations: [{d_min}, {d_max}]")
    def score(o):
        return scoring_model(weights['price'] * weighted_price(o['price'], p_min, p_max), 
                      weights['duration'] * weighted_duration(o['duration'], d_min, d_max),
                      weights['transfers'] * weighted_transfers(o['transfers'], t_min, t_max),
                      weighted_time(o), 
                      weighted_flexibility(o))

    return sorted(offers, key=score, reverse=True)

def scoring_model(w_price, w_duration, w_transfers, w_time, w_flexibility):
    score = w_price + w_duration + w_transfers + w_time + w_flexibility
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

def weighted_time(o):
    return 0.2

def weighted_flexibility(o):
    return 0.4

def lower_is_better(v, l, h):
    return 1.0 if l == h else (h - v) / (h - l)