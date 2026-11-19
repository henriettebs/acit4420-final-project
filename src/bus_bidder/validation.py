import re
from datetime import datetime, date

class InvalidIdentifierError(ValueError):
    """Raised when a booking or offer has an invalid id."""

class InvalidDateRangeError(ValueError):
    """Raised when a date is out of offers range."""

class InvalidOutOfRangeError(ValueError):
    """Raised when a value is out of range."""

def validate_search_query(departure_date, budget, max_transfers, changeable, refundable, min_customer_rating):
    try:
        departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date() # This checks if the entry is written on the correct format YYYY-MM-DD                
        if departure_date < date.today():
            raise InvalidDateRangeError(f"Departure date cannot be in the past. Please choose a date matching today ({date.today()}) or later.")
        if budget and not budget.isdigit():
            raise ValueError("Budget must be a positive number (int).")
        if max_transfers and not max_transfers.isdigit():
            raise ValueError("Transfers must be a positve number (int).")
        if changeable != 0 and changeable != 1:
            raise TypeError("Checkbox must be true or false.")
        if refundable != 0 and refundable != 1:
            raise TypeError("Checkbox must be true or false.")
        if min_customer_rating < 0:
            raise ValueError("Min customer rating must be a positive number.")
    except InvalidDateRangeError as e:
        return f"Date is out of range: {e}"
    except ValueError as e:
        return f"Incorrect value: {e}"
    except TypeError as e:
        return f"Incorrect type: {e}"

def validate_confirmation_query(booking_reference, name, email, phone_number, seats, seats_available):
    """Add ReGex expression for booking reference and traveller_email"""
    email_regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    phone_regex = r"^(?:[0-9\-\(\)\/\.]\s?){8,12}$"
    try:
        if booking_reference is None:
            raise InvalidIdentifierError("Booking reference was not created...")
        if not re.match(r"^0B[A-Za-z0-9]{8}$", booking_reference):
            raise InvalidIdentifierError("Booking reference does not match the format of '0B' + 8 letters/digits")
        if name is None or name == "":
            raise ValueError("Name cannot be empty.")
        if bool(re.search(r'\d', name)):
            raise TypeError("Name must be a string.")
        if email is None or email == "":
            raise ValueError("Email cannot be empty.")
        if not re.fullmatch(email_regex, email):
            raise ValueError("Email must be entered in correct format. (Ex: jane-smith@gmail.com)")
        if phone_number is None or phone_number == "":
            raise ValueError("Phone number cannot be empty.")
        if not re.fullmatch(phone_regex, phone_number):
            raise ValueError("Phone number must be entered with or without country code (47/0047)")
        if seats is None or seats == "" or seats == 0:
            raise ValueError("Atleast one seat must be booked.")
        if int(seats) > seats_available:
            raise InvalidOutOfRangeError(f"There is not enough available seats ({seats_available})")
    except InvalidIdentifierError as e:
        return f"The identifier is not recognizable: {e}"
    except InvalidOutOfRangeError as e:
        return f"Out of range: {e}"
    except ValueError as e:
        return f"Incorrect value: {e}"
    except TypeError as e:
        return f"Incorrect type: {e}"
    
def validate_company():
    print("company")

def validate_destination():
    print("destination")

def validate_offer(o):
    """Add ReGex expression for offer id"""
    date_pattern = r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
    try:
        offer_id = o['offer_id']
        destination = o['destination']
        travel_date = o['travel_date']
        arrival_date = o['arrival_date']
        departure_time = o['departure_time']
        price = o['price']
        duration = o['duration']
        changeable = o['changeability']
        refundable = o['refundability']
        available_seats = o['available_seats']
        customer_rating = float(o['customer_rating'])
        
        if not re.fullmatch(r"0F\d{4}", offer_id):
            raise InvalidIdentifierError("Offer ID does not match the format '0F\\d{4}'")
        if destination is None or destination == "":
            raise ValueError("Destination cannot be empty.")
        if not re.fullmatch(date_pattern, travel_date):
            raise ValueError(f"Date did not come in the correct format: YYYY-MM-DD, got {travel_date}")
        if re.fullmatch(date_pattern, travel_date):
            if date.fromisoformat(travel_date) < date.today():
                raise InvalidDateRangeError(f"Date cannot be in the past, got {travel_date}")
            if date.fromisoformat(arrival_date) < date.fromisoformat(travel_date):
                raise InvalidDateRangeError(f"Arrival date cannot be before departure date.")
        if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", departure_time):
            raise ValueError(f"Departure time must be HH:MM, got '{departure_time}'")
        if not re.fullmatch(r"\d+(\.\d+)?", str(price).strip()):
            raise ValueError(f"Price must use period as decimal separator, got {price}")
        if not duration.isdigit():
            raise ValueError(f"Duration must be a number, got {duration}")
        if changeable not in ("True", "False") or refundable not in ("True", "False"):
            raise ValueError("Not boolean value.")
        if int(available_seats) <= 0:
            raise InvalidOutOfRangeError("There must be available seats on the offer.")
        if customer_rating <= 0.0 or customer_rating > 5.0:
            raise InvalidOutOfRangeError(f"Customer rating must be withing range (0, 5).")
    except InvalidIdentifierError as e:
        return f"The identifier is not recognizable: {e}"
    except InvalidOutOfRangeError as e:
        return f"Out of range: {e}"
    except InvalidDateRangeError as e:
        return f"Date is out of range: {e}"
    except ValueError as e:
        return f"Incorrect value: {e}"

