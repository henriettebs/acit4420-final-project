from datetime import date, time

class Descriptor:
    def __get__(self, instance, owner):
        return instance._name
    
    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        instance._name = value # set name

"""Models for the bus bidder application."""
class Traveller:
    """Represents a traveller in the bus bidder application."""
    name = Descriptor()

    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"Traveller - Name: {self.name}, Email: {self.email}, Phone: {self.phone}"
    
    def compare_traveller_names(self, value):
        if value == self.name:
            return self
    
class Destination:
    """Represents a destination and it's distance from Madrid."""

    def __init__(self, city: str, distance_km: int, coastal_city: bool, major_city: bool):
        self.city = city
        self.distance_km = int(distance_km)
        self.coastal_city = str(coastal_city).strip().lower() == "true"
        self.major_city = str(major_city).strip().lower() == "true"

class Company:
    """Represents a bus company in the bus bidder application."""

    def __init__(self, name: str, suggested_profile: str, base_price_per_km: float, average_speed: float, max_passengers: int, luggage_limit_kg: int, amenities: str, changeable: bool, refundable: bool, eco_friendly: bool, base_rating: float, co2_per_km: float):
        self.name = name
        self.suggested_profile = suggested_profile
        self.base_price_per_km = float(base_price_per_km)
        self.average_speed = float(average_speed)
        self.max_passengers = int(max_passengers)
        self.luggage_limit_kg = int(luggage_limit_kg)
        self.amenities = amenities
        self.changeable = str(changeable).strip().lower() == "true"
        self.refundable = str(refundable).strip().lower() == "true"
        self.eco_friendly = eco_friendly
        self.base_rating = float(base_rating)
        self.co2_per_km = float(co2_per_km)

    def __str__(self):
        return f"Company {self.name} with {self.suggested_profile}."
    
    def compare_company_names(self, value):
        if value == self.name:
            return self

class Booking:
    """Represents a booking made by a traveller with a bus company."""

    def __init__(self, booking_reference: str, traveller: Traveller, offer: Offer, seats_booked: int):
        self.booking_reference = booking_reference
        self.traveller = traveller
        self.offer = offer
        self.seats_booked = seats_booked

    def __str__(self):
        return f"Booking - Traveller: {self.traveller.name}, Company: {self.offer.company.name}, Seats Booked: {self.seats_booked}"

class Bid:
    """Represents a bid or search-query from the traveller."""

    def __init__(self, departure_date: date, departure_time: time, departure_city: str, arrival_city: str, budget: float, max_transfers: int, changeable: bool, refundable: bool, min_customer_rating: float):
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.budget = self.convert_to_float(budget)
        self.max_transfers = self.convert_to_int(max_transfers)
        self.changeable = bool(changeable)
        self.refundable = bool(refundable)
        self.min_customer_rating = self.convert_to_float(min_customer_rating)

    def convert_to_float(self, value):
        if value == None or value == "":
            return 0.0
        return float(value)
    
    def convert_to_int(self, value):
        if value == None or value == "":
            return 100 # All transfers are possible
        return int(value)

class Offer:
    """Represents a possible journey for a traveller with a bus company."""

    def __init__(self, offer_id: str, company: Company, journey: Journey, price: float, luggage_allowance: int, changeability: bool, refundability: bool, available_seats: int, customer_rating: float, ranking: dict):
        self.offer_id = offer_id
        self.company = company
        self.journey = journey
        self.price = float(price) # Converts csv string to float value
        self.luggage_allowance = int(luggage_allowance) # Converts csv string to int value
        self.changeability = str(changeability).strip().lower() == "true" # Checks if string is 'true', and converts to boolean value
        self.refundability = str(refundability).strip().lower() == "true" # Checks if string is 'true', and converts to boolean value
        self.available_seats = int(available_seats)
        self.customer_rating = float(customer_rating)
        self.ranking = ranking

    def __str__(self):
            return (f"Offer - Company: {self.company_name}, Destination: {self.destination}, Travel Date: {self.journey.travel_date}, "
                    f"Departure Time: {self.journey.departure_time}, Arrival Time: {self.journey.arrival_time}, Duration: {self.journey.duration} mins, "
                    f"Price: €{self.price:.2f}, Transfers: {self.transfers}, Luggage Allowance: {self.luggage_allowance} kg, "
                    f"Changeability: {'Yes' if self.changeability else 'No'}, Refundability: {'Yes' if self.refundability else 'No'}, "
                    f"Available Seats: {self.available_seats}, Customer Rating: {self.customer_rating}/5, Environmental Measure: {self.journey.environmental_measure}")
    """List all relevant properties accessed through Offer and make them available on Offer objects"""
    @property
    def company_name(self):
        return self.company.name
    """List all properties accessed through Journey and make them available on Offer objects"""
    @property
    def destination(self):
        return self.journey.destination.city
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
    
    def set_ranking(self, ranking_dict):
        self.ranking = ranking_dict

    def get_co2_emissions(self):
        km = self.journey.destination.distance_km
        co2_per_km = self.company.co2_per_km
        co2_emission = km * co2_per_km
        
        return co2_emission

class Journey:
    """Represents a journey and its details"""
    def __init__(self, destination: Destination, travel_date: str, departure_time: str, arrival_time: str, arrival_date: str, duration: int, transfers: int, environmental_measure: str):
        self.destination = destination
        self.travel_date: date = date.fromisoformat(travel_date)
        self.departure_time = time.fromisoformat(departure_time)
        self.arrival_time = time.fromisoformat(arrival_time)
        self.arrival_date = date.fromisoformat(arrival_date)
        self.duration = int(duration)
        self.transfers = int(transfers)
        self.environmental_measure = environmental_measure
    
    """List properties accessed through Destination and make them available on Journey objects"""
    @property
    def destination_name(self):
        return self.destination.city
    @property
    def distance_km(self):
        return self.destination.distance_km
    
    def minutes_to_hours(self):
        """Convert duration in minutes to hours and minutes."""
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"