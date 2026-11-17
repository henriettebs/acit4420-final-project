from datetime import date, time
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

    def __init__(self, name: str, suggested_profile: str, base_price_per_km: float, average_speed: float, max_passengers: int, luggage_limit_kg: int, amenities: str, changable: bool, refundable: bool, eco_friendly: bool, base_rating: float, co2_per_km: float):
        self.name = name
        self.suggested_profile = suggested_profile
        self.base_price_per_km = base_price_per_km
        self.average_speed = average_speed
        self.max_passengers = max_passengers
        self.luggage_limit_kg = luggage_limit_kg
        self.amenities = amenities
        self.changable = changable
        self.refundable = refundable
        self.eco_friendly = eco_friendly
        self.base_rating = base_rating
        self.co2_per_km = co2_per_km

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

    def __init__(self, offer_id: str, company: str, journey: Journey, price: float, luggage_allowance: int, changeability: bool, refundability: bool, available_seats: int, customer_rating: float):
        self.offer_id = offer_id
        self.company = company
        self.journey = journey
        self.price = float(price) # Converts csv string to float value
        self.luggage_allowance = int(luggage_allowance) # Converts csv string to int value
        self.changeability = str(changeability).strip().lower() == "true" # Checks if string is 'true', and converts to boolean value
        self.refundability = str(refundability).strip().lower() == "true" # Checks if string is 'true', and converts to boolean value
        self.available_seats = int(available_seats)
        self.customer_rating = float(customer_rating)

    def __str__(self):
            return (f"Offer - Company: {self.company}, Destination: {self.journey.destination}, Travel Date: {self.journey.travel_date}, "
                    f"Departure Time: {self.journey.departure_time}, Arrival Time: {self.journey.arrival_time}, Duration: {self.journey.duration} mins, "
                    f"Price: €{self.price:.2f}, Transfers: {self.transfers}, Luggage Allowance: {self.luggage_allowance} kg, "
                    f"Changeability: {'Yes' if self.changeability else 'No'}, Refundability: {'Yes' if self.refundability else 'No'}, "
                    f"Available Seats: {self.available_seats}, Customer Rating: {self.customer_rating}/5, Environmental Measure: {self.journey.environmental_measure}")
    
    """List all properties accessed through Journey and make them available on Offer objects"""
    @property
    def destination(self):
        return self.journey.destination
    @property
    def travel_date(self):
        return self.journey.travel_date
    @property
    def departure_time(self):
        return self.journey.departure_time
    @property
    def arrival_time(self):
        return self.journey.arrival_time
    @property
    def arrival_date(self):
        return self.journey.arrival_date
    @property
    def duration(self):
        return self.journey.duration
    @property
    def transfers(self):
        return self.journey.transfers
    @property
    def environmental_measure(self):
        return self.journey.environmental_measure
    
    
    

class Journey:
    """Represents a journey and its details"""
    def __init__(self, destination: str, travel_date: str, departure_time: str, arrival_time: str, arrival_date: str, duration: int, transfers: int, environmental_measure: str):
        self.destination = destination
        self.travel_date: date = date.fromisoformat(travel_date)
        self.departure_time = time.fromisoformat(departure_time)
        self.arrival_time = time.fromisoformat(arrival_time)
        self.arrival_date = date.fromisoformat(arrival_date)
        self.duration = int(duration)
        self.transfers = int(transfers)
        self.environmental_measure = environmental_measure
    
    def minutes_to_hours(self):
        """Convert duration in minutes to hours and minutes."""
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"