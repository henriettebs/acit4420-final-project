"""Generate offers.csv file based on companies.csv and destinations.csv."""
import csv
import random
from datetime import date, datetime, timedelta

DEPARTURE_HOURS = {
    "SolRuta": [8, 10, 12, 14, 16],
    "Camino Express": [7, 9, 11, 13, 15, 17, 19, 21],
    "CostaLink": [6, 9, 12, 15, 18, 21],
    "VerdeBus": [8, 10, 12, 14, 16],
    "NocheVia": [1, 2, 4, 20, 22, 23]
}

rng = random.Random(42)
START_DATE = date(2026,11,19)
END_DATE = date(2027,1,2)

def to_bool(value):
    """Convert a string to a boolean."""
    return value.lower()  == 'true'

def read_csv(path):
    """Read a CSV file and return a list of dictionaries."""
    with open(path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
    
def company_serves(company, destination):
    """Decide if a company serves a given destination based on its profile."""
    name = company['company']
    if name == "Camino Express":
        return to_bool(destination["major_city"])
    if name == "CostaLink":
        return to_bool(destination["coastal"]) or rng.random() < 0.5
    return True

def generate_transfers(company, destination, km):
    """Generate a number of transfers based on company profile and distance."""
    name = company['company']
    if name == "SolRuta":
        return 0 if km < 300 else rng.randint(1, 3)
    if name == "Camino Express":
        return 0
    if name == "CostaLink":
        return 0 if to_bool(destination["coastal"]) else rng.randint(1, 2)
    if name == "VerdeBus":
        return rng.randint(0, 2)
    if name == "NocheVia":
        return rng.randint(0, 1)
    return rng.randint(0, 3)

def create_dates(start, end):
    """Create a list of possbile dates for travel."""
    return [start + timedelta(days=i) for i in range((end-start).days + 1)]

def get_companies():
    companies = read_csv('bus_bidder/data/companies.csv')
    return companies

def get_destinations():
    destinations = read_csv('bus_bidder/data/destinations.csv')
    return destinations

def generate_offers():
    companies = get_companies()
    destinations = get_destinations()
    rows, n = [], 1
    travel_dates = create_dates(START_DATE, END_DATE)

    for c in companies:
        name = c['company']
        for d in destinations:
            destination = d['city']
            if not company_serves(c, d):
                continue
            km = float(d['distance_from_madrid_km'])
            for dt in travel_dates:
                for hour in rng.sample(DEPARTURE_HOURS[name], k=2): # Pick 2 random departure times for each date
                    dep = datetime.fromisoformat(f"{dt}T{hour:02d}:{rng.choice([0, 15, 30, 45]):02d}") # Randomize minutes to 0, 15, 30, or 45
                    transfers = generate_transfers(c, d, km)
                    duration = int(km / float(c['average_speed']) * 60 + transfers * rng.randint(5, 60)) # Add 5-60 minutes for each transfer
                    arr = dep + timedelta(minutes=duration)
                    base_price = km * float(c['base_price_per_km']) * rng.uniform(0.9, 1.1) # Add some randomness to the price

                    rows.append({
                        "offer_id": f"0F{n:04d}", # Unique offer ID - zero-padded
                        "company": name,
                        "destination": destination,
                        "travel_date": dt.isoformat(),
                        "departure_time": dep.strftime("%H:%M"),
                        "arrival_time": arr.strftime("%H:%M"),
                        "arrival_date": arr.date().isoformat(),
                        "duration": duration,
                        "price": round(base_price, 2),
                        "transfers": transfers,
                        "luggage_allowance": int(c['luggage_limit_kg']),
                        "changeability": to_bool(c['changeable']),
                        "refundability": to_bool(c['refundable']),
                        "available_seats": rng.randint(1, int(c['max_passengers'])),
                        "customer_rating": round(float(c['base_rating']) + rng.uniform(-0.5, 0.5), 1), # Add some randomness to the rating
                        "environmental_measure": "Eco-friendly" if to_bool(c['eco_friendly']) else "Standard"
                    })
                    n += 1
    rows, error_log = inject_errors(rows, error_rate=0.05)

    out_path = 'bus_bidder/data/offers.csv'

    with open('bus_bidder/data/offers.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["offer_id", "company", "destination", "travel_date", "departure_time", "arrival_time", "arrival_date", "duration", "price", "transfers", "luggage_allowance", "changeability", "refundability", "available_seats", "customer_rating", "environmental_measure"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open('bus_bidder/data/offers_errors.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["offer_id", "field", "error_type", "bad_value"])
        writer.writeheader()
        writer.writerows(error_log)

    print(f"Wrote {len(rows)} offers ({len(error_log)} with errors) to {out_path}")

def inject_errors(rows, error_rate):
    err_rng = random.Random(7)       # separate seed
    log = []

    def bad_offer_id(r):     r["offer_id"] = "XX" + r["offer_id"][2:]
    def bad_date_format(r):  r["travel_date"] = r["travel_date"].replace("-", "/")
    def impossible_date(r):  r["travel_date"] = "2026-13-45"
    def past_date(r):        r["travel_date"] = "2020-01-01"
    def negative_price(r):   r["price"] = -abs(float(r["price"]))
    def word_price(r):       r["price"] = "hundred"
    def comma_price(r):      r["price"] = str(r["price"]).replace(".", ",")
    def missing_dest(r):     r["destination"] = ""
    def bad_time(r):         r["departure_time"] = "25:61"
    def bad_rating(r):       r["customer_rating"] = 7.3
    def negative_seats(r):   r["available_seats"] = -2
    def bad_bool(r):         r["refundability"] = "maybe"
    def bad_duration(r):     r["duration"] = "abc"
    def arrival_before(r):   r["arrival_date"] = "2020-01-01"

    errors = {
        "bad_offer_id": ("offer_id", bad_offer_id),
        "bad_date_format": ("travel_date", bad_date_format),
        "impossible_date": ("travel_date", impossible_date),
        "past_date": ("travel_date", past_date),
        "negative_price": ("price", negative_price),
        "word_price": ("price", word_price),
        "comma_price": ("price", comma_price),
        "missing_destination": ("destination", missing_dest),
        "bad_time": ("departure_time", bad_time),
        "bad_rating": ("customer_rating", bad_rating),
        "negative_seats": ("available_seats", negative_seats),
        "bad_bool": ("refundability", bad_bool),
        "bad_duration": ("duration", bad_duration),
        "arrival_before_departure": ("arrival_date", arrival_before),
    }

    for r in rows:
        if err_rng.random() < error_rate:
            name = err_rng.choice(list(errors))
            field, corrupt = errors[name]
            corrupt(r)
            log.append({"offer_id": r["offer_id"], "field": field,
                        "error_type": name, "bad_value": r[field]})

    # One duplicate offer ID, to test uniqueness checks
    if len(rows) > 10:
        dup = err_rng.choice(rows[1:])
        original_id = dup["offer_id"]
        dup["offer_id"] = rows[0]["offer_id"]
        log.append({"offer_id": rows[0]["offer_id"], "field": "offer_id",
                    "error_type": "duplicate_id", "bad_value": f"{original_id} -> {dup['offer_id']}"})

    return rows, log
