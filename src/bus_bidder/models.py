"""Models for the bus bidder application."""

class Traveller:
    """Represents a traveller in the bus bidder application."""

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __str__(self):
        return f"Traveller - Name: {self.name}, Email: {self.email}"
    
class Company:
    """Represents a bus company in the bus bidder application."""

    def __init__(self, name: str, suggested_profile: str):
        self.name = name
        self.suggested_profile = suggested_profile

    def __str__(self):
        return f"Company {self.name} with {self.suggested_profile}."

class Booking:
    """Represents a booking made by a traveller with a bus company."""

    def __init__(self, traveller: Traveller, offer: Offer, seats_booked: int):
        self.traveller = traveller
        self.offer = offer
        self.seats_booked = seats_booked

    def __str__(self):
        return f"Booking - Traveller: {self.traveller.name}, Company: {self.offer.company.name}, Seats Booked: {self.seats_booked}"
    
class Offer:
    """Represents a possible journey for a traveller with a bus company."""

    def __init__(self, company: Company, journey: Journey, price: float, luggage_allowance: int, changeability: bool, refundability: bool, available_seats: int, customer_rating: float):
        self.company = company
        self.journey = journey
        self.price = price
        self.luggage_allowance = luggage_allowance
        self.changeability = changeability
        self.refundability = refundability
        self.available_seats = available_seats
        self.customer_rating = customer_rating

    def __str__(self):
            return (f"Offer - Company: {self.company.name}, Destination: {self.journey.destination}, Travel Date: {self.journey.travel_date}, "
                    f"Departure Time: {self.journey.departure_time}, Arrival Time: {self.journey.arrival_time}, Duration: {self.journey.duration} mins, "
                    f"Price: €{self.price:.2f}, Transfers: {self.transfers}, Luggage Allowance: {self.luggage_allowance} kg, "
                    f"Changeability: {'Yes' if self.changeability else 'No'}, Refundability: {'Yes' if self.refundability else 'No'}, "
                    f"Available Seats: {self.available_seats}, Customer Rating: {self.customer_rating}/5, Environmental Measure: {self.journey.environmental_measure}")

class Journey:
    """Represents a journey and its details"""
    def __init__(self, destination: str, travel_date: str, departure_time: str, arrival_time: str, duration: int, transfers: int, environmental_measure: str):
        self.destination = destination
        self.travel_date = travel_date
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration
        self.transfers = transfers
        self.environmental_measure = environmental_measure