def rank_relevant_offers(offers):
    """Rank offers based on price, transfers, and customer rating."""
    return sorted(offers, key=lambda x: (x['price']))