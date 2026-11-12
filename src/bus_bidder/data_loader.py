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
test_date_outbound = date.today()
test_date_inbound = date.today() + timedelta(days=7)
#res_dates = [test_date_outbound, test_date_outbound + timedelta(days=1), test_date_inbound, test_date_inbound + timedelta(days=1)]

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

def create_dates(date_outbound, date_inbound):
    """Create a list of possbile dates for travel."""
    today = date.today()
    return [today + timedelta(days=i) for i in range(30)]


def generate_offers(res_dates):
    companies = read_csv('bus_bidder/data/companies.csv')
    destinations = read_csv('bus_bidder/data/destinations.csv')
    rows, n = [], 1

    for c in companies:
        name = c['company']
        #print(f"Generating offers for {name}...")
        for d in destinations:
            destination = d['city']
            if not company_serves(c, d):
                #print(f"Skipping {name} for {destination} (does not serve this destination).")
                continue
            km = float(d['distance_from_madrid_km'])
            #print(f"Iterating over destination: {destination} ({km} km)")
            for date in res_dates:
                #print(f"Generating offers for date: {date}")
                for hour in rng.sample(DEPARTURE_HOURS[name], k=2): # Pick 2 random departure times for each date
                    dep = datetime.fromisoformat(f"{date}T{hour:02d}:{rng.choice([0, 15, 30, 45]):02d}") # Randomize minutes to 0, 15, 30, or 45
                    transfers = generate_transfers(c, d, km)
                    duration = int(km / float(c['average_speed']) * 60 + transfers * rng.randint(5, 60)) # Add 5-60 minutes for each transfer
                    arr = dep + timedelta(minutes=duration)
                    base_price = km * float(c['base_price_per_km']) * rng.uniform(0.9, 1.1) # Add some randomness to the price

                    rows.append({
                        "offer_id": f"0F{n:04d}", # Unique offer ID - zero-padded
                        "company": name,
                        "destination": destination,
                        "travel_date": date.isoformat(),
                        "departure_time": dep.strftime("%H:%M"),
                        "arrival_time": arr.strftime("%H:%M"),
                        "arrival_date": arr.date().isoformat(),
                        "duration": duration,
                        "price": round(base_price, 2),
                        "transfers": transfers,
                        "luggage_allowance": int(c['luggage_limit_kg']),
                        "changeability": to_bool(c['changable']),
                        "refundability": to_bool(c['refundable']),
                        "available_seats": rng.randint(1, int(c['max_passengers'])),
                        "customer_rating": round(float(c['base_rating']) + rng.uniform(-0.5, 0.5), 1), # Add some randomness to the rating
                        "environmental_measure": "Eco-friendly" if to_bool(c['eco_friendly']) else "Standard"
                    })
                    n += 1

    with open('bus_bidder/data/offers.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["offer_id", "company", "destination", "travel_date", "departure_time", "arrival_time", "arrival_date", "duration", "price", "transfers", "luggage_allowance", "changeability", "refundability", "available_seats", "customer_rating", "environmental_measure"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} offers to bus_bidder/data/offers.csv")

