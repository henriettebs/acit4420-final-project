import csv
import os

def write_booking(booking):
    fieldnames = ["booking_reference", "traveller_name", "traveller_email", "traveller_phone", 
                  "offer_id", "company", "departure_city", "arrival_city", "departure_date", 
                  "departure_time", "arrival_date", "arrival_time", "duration", "transfers", 
                  "environmental_measure", "price", "luggage_allowance", "changeability", 
                  "flexibility", "available_seats", "customer_rating", "seats_booked"]
    t = booking.traveller
    o = booking.offer
    j = o.journey

    updated_available_seats = o.available_seats - int(booking.seats_booked)

    row = {
        "booking_reference": booking.booking_reference, 
        "traveller_name": t.name, 
        "traveller_email": t.email, 
        "traveller_phone": t.phone, 
        "offer_id": o.offer_id, 
        "company": o.company, 
        "departure_city": "Madrid", 
        "arrival_city": j.destination, 
        "departure_date": j.travel_date, 
        "departure_time": j.departure_time, 
        "arrival_date": j.arrival_date, 
        "arrival_time": j.arrival_time, 
        "duration": j.duration, 
        "transfers": j.transfers, 
        "environmental_measure": j.environmental_measure, 
        "price": o.price, 
        "luggage_allowance": o.luggage_allowance, 
        "changeability": o.changeability, 
        "flexibility": o.refundability, 
        "available_seats": updated_available_seats, 
        "customer_rating": o.customer_rating, 
        "seats_booked": booking.seats_booked
    }

    path = 'bus_bidder/data/bookings.csv'
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0

    with open(path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def write_invalid_offer(offer):
    fieldnames = ["offer_id", "company", "destination", "travel_date", "departure_time", "arrival_time", 
                  "arrival_date", "duration", "price", "transfers", "luggage_allowance", "changeability", 
                  "refundability", "available_seats", "customer_rating", "environmental_measure"]
    
    row = {
        "offer_id": offer['offer_id'], 
        "company": offer['company'], 
        "destination": offer['destination'], 
        "travel_date": offer['travel_date'], 
        "departure_time": offer['departure_time'], 
        "arrival_time": offer['arrival_time'], 
        "arrival_date": offer['arrival_date'], 
        "duration": offer['duration'], 
        "price": offer['price'], 
        "transfers": offer['transfers'], 
        "luggage_allowance": offer['luggage_allowance'], 
        "changeability": offer['changeability'], 
        "refundability": offer['refundability'], 
        "available_seats": offer['available_seats'],
        "customer_rating": offer['customer_rating'], 
        "environmental_measure": offer['environmental_measure']
    }
    path = 'bus_bidder/data/invalid_offers.csv'
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0

    with open(path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def write_ranking(offers):
    fieldnames = ["offer_id", "company", "destination", "travel_date", "departure_time", "arrival_time", 
                  "arrival_date", "duration", "price", "transfers", "luggage_allowance", "changeability", 
                  "refundability", "available_seats", "customer_rating", "rank_score", "price_weight",
                  "duration_weight", "transfer_weight", "time_weight", "flex_weight"]
     
    path = 'bus_bidder/data/ranked_offers.csv'
    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for offer in offers:
            print("OFFER: ", offer.ranking)
            row = {
                "offer_id": offer.offer_id, 
                "company": offer.company.name, 
                "destination": offer.destination, 
                "travel_date": offer.travel_date, 
                "departure_time": offer.departure_time, 
                "arrival_time": offer.arrival_time, 
                "arrival_date": offer.arrival_date, 
                "duration": offer.duration, 
                "price": offer.price, 
                "transfers": offer.transfers, 
                "luggage_allowance": offer.luggage_allowance, 
                "changeability": offer.changeability, 
                "refundability": offer.refundability, 
                "available_seats": offer.available_seats,
                "customer_rating": offer.customer_rating, 
                "rank_score": offer.ranking['total_score'],
                "price_weight": offer.ranking['price_weight'],
                "duration_weight": offer.ranking['duration_weight'],
                "transfer_weight": offer.ranking['transfer_weight'],
                "time_weight": offer.ranking['time_weight'],
                "flex_weight": offer.ranking['flex_weight']

            }
            writer.writerow(row)
    