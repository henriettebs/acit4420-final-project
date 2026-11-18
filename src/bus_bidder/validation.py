import re
from datetime import datetime, date

class InvalidIdentifierError(ValueError):
    """Raised when a booking or offer has an invalid id."""

class InvalidDateRangeError(ValueError):
    """Raised when a date is out of offers range."""

def validate_search_query(departure_date, budget, max_transfers, changeable, refundable, min_customer_rating):
    print("Will be validating: ", departure_date, budget,  max_transfers, changeable, refundable, min_customer_rating)
    try:
        departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date() # This checks if the entry is written on the correct format YYYY-MM-DD        
        print("min_customer_rating", min_customer_rating)
        
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
    #except Exception as e:
        #print(type(e).__name__, e)
    except InvalidIdentifierError as e:
        return f"The identifier is not recognizable: {e}"
    except InvalidDateRangeError as e:
        return f"Date is out of range: {e}"
    except ValueError as e:
        return f"Incorrect value: {e}"
    except TypeError as e:
        return f"Incorrect type: {e}"

def validate_confirmation_query(name, email, phone_number, seats, seats_available):
    """Add ReGex expression for booking reference and traveller_email"""
    print("yeah")
    try:
        

def validate_company():
    print("company")

def validate_destination():
    print("destination")

def validate_offer():
    """Add ReGex expression for offer id"""
    print("offer")

