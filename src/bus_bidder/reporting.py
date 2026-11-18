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
