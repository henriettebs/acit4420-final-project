import customtkinter as ctk
from bus_bidder.data_loader import generate_offers
from bus_bidder.filtering import filter_relevant_offers
from bus_bidder.ranking import rank_relevant_offers
from datetime import date, datetime, timedelta
import csv

ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

class BusBidderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bus Bidder")
        self.geometry("800x800")

        label = ctk.CTkLabel(self, text="Welcome to Bus Bidder!", font=("Arial", 16))
        label.pack(pady=10)

        travel_times = ["Any", "Morning (6-12)", "Afternoon (12-18)", "Evening (18-24)", "Night (0-6)"]    
        # Group departure and return date and time inputs in a frame
        departure_frame = ctk.CTkFrame(self)
        departure_frame.pack(pady=10, padx=10, fill="x")
        #return_frame = ctk.CTkFrame(self)
        #return_frame.pack(pady=10, padx=10, fill="x")
        # Departure label
        departure_label = ctk.CTkLabel(departure_frame, text="Departure Date and Time", font=("Arial", 14))
        departure_label.grid(row=0, column=0, padx=10, sticky="w")
        # Departure date and time entries
        self.departure_entry = ctk.CTkEntry(departure_frame, placeholder_text="YYYY-MM-DD")
        self.departure_time = ctk.CTkOptionMenu(departure_frame, values=travel_times, command=self.on_departure_time_change)
        self.departure_entry.grid(row=1, column=0, padx=10, pady=5)
        self.departure_time.grid(row=1, column=1, padx=10, pady=5)
        #self.return_checkbox = ctk.CTkCheckBox(departure_frame, text="Return Trip", font=("Arial", 12), command=self.toggle_return_trip)
        #self.return_checkbox.grid(row=1, column=2, padx=10, pady=5)
        # Return label
        #return_label = ctk.CTkLabel(return_frame, text="Return Date and Time", font=("Arial", 14))
        #return_label.grid(row=0, column=0, padx=10, sticky="w")
        # Return date and time entries
        #self.return_entry = ctk.CTkEntry(return_frame, placeholder_text="YYYY-MM-DD")
        #self.return_time = ctk.CTkOptionMenu(return_frame, values=travel_times, command=self.on_return_time_change)
        #self.return_entry.grid(row=1, column=0, padx=10, pady=5)
        #self.return_time.grid(row=1, column=1, padx=10, pady=5)
        #self.return_entry.configure(state="disabled")
        #self.return_time.configure(state="disabled")

        # Group departure and arrival city option menus in a frame
        city_frame = ctk.CTkFrame(self)
        city_frame.pack(pady=10, padx=10, fill="x")
        # Departure city label
        depature_city_label = ctk.CTkLabel(city_frame, text="Departure City", font=("Arial", 14))
        depature_city_label.grid(row=0, column=0, padx=10, sticky="w")
        # Arrival city label
        arrival_city_label = ctk.CTkLabel(city_frame, text="Arrival City", font=("Arial", 14))
        arrival_city_label.grid(row=0, column=1, padx=10, sticky="w")
        # Departure and arrival city option menus
        city_options = self.get_city_options()
        self.departure_city = ctk.CTkOptionMenu(city_frame, values=["Madrid"])
        self.departure_city.grid(row=1, column=0, padx=10, pady=5)
        self.arrival_city = ctk.CTkOptionMenu(city_frame, values=city_options, command=self.on_arrival_city_change)
        self.arrival_city.grid(row=1, column=1, padx=10, pady=5)

        # Group budget, transfers, changeability, and refundability inputs in a frame
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=10, padx=10, fill="x")
        # Budget label and entry
        budget_label = ctk.CTkLabel(options_frame, text="Budget (€)", font=("Arial", 14))
        budget_label.grid(row=0, column=0, padx=10, sticky="w")
        self.budget_entry = ctk.CTkEntry(options_frame, placeholder_text="Enter your budget")
        self.budget_entry.grid(row=1, column=0, padx=10, pady=5)
        # Transfers label and entry
        transfers_label = ctk.CTkLabel(options_frame, text="Max Transfers", font=("Arial", 14))
        transfers_label.grid(row=0, column=1, padx=10, sticky="w")
        self.transfers_entry = ctk.CTkEntry(options_frame, placeholder_text="Enter max transfers")
        self.transfers_entry.grid(row=1, column=1, padx=10, pady=5)
        # Requirements label and checkboxes
        requirements_label = ctk.CTkLabel(options_frame, text="Offer requirements", font=("Arial", 14))
        requirements_label.grid(row=0, column=2, padx=10, sticky="w")
        self.changeability_checkbox = ctk.CTkCheckBox(options_frame, text="Changeable", font=("Arial", 12))
        self.changeability_checkbox.grid(row=1, column=2, padx=10, pady=5)
        self.refundability_checkbox = ctk.CTkCheckBox(options_frame, text="Refundable", font=("Arial", 12))
        self.refundability_checkbox.grid(row=1, column=3, padx=10, pady=5)
        # Customer rating label and slider
        rating_label = ctk.CTkLabel(options_frame, text="Min. Customer Rating", font=("Arial", 14))
        rating_label.grid(row=0, column=4, padx=10, sticky="w")
        self.slider = ctk.CTkSlider(options_frame, from_=0, to=5, number_of_steps=5, command=self.on_slider_change, width=150)
        self.slider.grid(row=1, column=4, padx=10, pady=5)
        self.slider_label = ctk.CTkLabel(options_frame, text="2.5", font=("Arial", 14))
        self.slider_label.grid(row=1, column=5, padx=10, pady=5)

        button = ctk.CTkButton(self, text="Search", command=self.on_button_click)
        button.pack(pady=10)

    def on_button_click(self):
        print(f"Bid was submitted!")
        #print(f"Return date:", self.return_entry.get())
        try:
            departure_date = datetime.strptime(self.departure_entry.get(), "%Y-%m-%d").date()
            #if self.return_entry.get() != "":
                #return_date = datetime.strptime(self.return_entry.get(), "%Y-%m-%d").date()
            #elif self.return_entry.get() == "":
                #return_date = None
            if departure_date < date.today():
                print("Departure date cannot be in the past.")
            #elif return_date is not None and return_date < departure_date:
                #print("Return date cannot be before departure date.")
            else:
                print(f"Departure Date and Time: {departure_date} {self.departure_time.get()}")
                #print(f"Return Date and Time: {return_date} {self.return_time.get()}")
                print(f"Travel from {self.departure_city.get()} to {self.arrival_city.get()}")

            bid = {
                "departure_date": departure_date,
                "departure_time": self.departure_time.get(),
                #"return_date": return_date,
                #"return_time": self.return_time.get(),
                "departure_city": self.departure_city.get(),                    
                "arrival_city": self.arrival_city.get(),
                "budget": self.budget_entry.get(),
                "max_transfers": self.transfers_entry.get(),
                "changeable": self.changeability_checkbox.get(),
                "refundable": self.refundability_checkbox.get(),
                "min_customer_rating": self.slider.get()
            }
            self.search_offers(bid)

        except ValueError as e:
            print(f"{e} -> Invalid date format. Please use YYYY-MM-DD.")

    def get_city_options(self):
        with open('bus_bidder/data/destinations.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row['city'] for row in reader]

    def on_arrival_city_change(self, selected_city):
        print(f"Selected arrival city: {selected_city}")

    def on_departure_time_change(self, selected_time):
        print(f"Selected departure time: {selected_time}")

    def on_return_time_change(self, selected_time):
        print(f"Selected return time: {selected_time}")

    def on_slider_change(self, value):
        self.slider_label.configure(text=f"{value:.1f}")

    """def toggle_return_trip(self):
        if self.return_checkbox.get():
            self.return_entry.configure(state="normal")
            self.return_time.configure(state="normal")
        else:
            self.return_entry.delete(0, "end") # Removes any text in the return date entry when the checkbox is unchecked
            self.return_entry.configure(state="disabled")
            self.return_time.configure(state="disabled")"""
    
    def search_offers(self, bid):
        print("Searching for offers with the following criteria:")
        for key, value in bid.items():
            print(f"{key}: {value}")
        # Here you would implement the logic to search for offers based on the bid criteria.
        # This could involve filtering a list of offers, querying a database, etc.
        # For now, we'll just print a placeholder message.

        # open new window with search results
        travel_date = bid["departure_date"]
        travel_dates = [travel_date, travel_date + timedelta(days=1)]  # Add the departure date to the list
        generate_offers(travel_dates)
        self.open_results_window(bid)
    
    def open_results_window(self, bid):
        results_window = ctk.CTkToplevel(self)
        results_window.title("Search Results")
        results_window.geometry("800x800")

        label = ctk.CTkLabel(results_window, text="Search Results", font=("Arial", 16))
        label.pack(pady=10)

        filtered_offers = filter_relevant_offers(self.get_all_offers(), bid)
        print(f"Found {len(filtered_offers)} relevant offers.")
        ranked_offers = rank_relevant_offers(filtered_offers)
        for o in ranked_offers:
            print(f"Ranked offers: {o["offer_id"]} {o["company"]} to {o["destination"]} with price {o["price"]} and rating {o["customer_rating"]}")
    
    def get_all_offers(self):
        with open('bus_bidder/data/offers.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]

if __name__ == "__main__":
    app = BusBidderApp()
    app.mainloop()