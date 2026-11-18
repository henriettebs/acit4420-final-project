import customtkinter as ctk
from bus_bidder.data_loader import generate_offers
from bus_bidder.filtering import filter_relevant_offers
from bus_bidder.ranking import rank_relevant_offers, get_cheapest_route, get_shortest_route, get_best_rated_route
from bus_bidder.models import Traveller, Company, Booking, Offer, Journey, Bid
from bus_bidder.reporting import write_booking
from bus_bidder.validation import validate_search_query, validate_confirmation_query
from datetime import date, datetime, timedelta
import csv
import uuid

ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"
color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]

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
        # Departure label
        departure_label = ctk.CTkLabel(departure_frame, text="Departure Date and Time", font=("Arial", 14))
        departure_label.grid(row=0, column=0, padx=10, sticky="w")
        # Departure date and time entries
        self.departure_entry = ctk.CTkEntry(departure_frame, placeholder_text="YYYY-MM-DD")
        self.departure_time = ctk.CTkOptionMenu(departure_frame, values=travel_times, command=self.on_departure_time_change)
        self.departure_entry.grid(row=1, column=0, padx=10, pady=5)
        self.departure_time.grid(row=1, column=1, padx=10, pady=5)

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
        self.slider = ctk.CTkSlider(options_frame, from_=0, to=5, number_of_steps=10, command=self.on_slider_change, width=150)
        self.slider.grid(row=1, column=4, padx=10, pady=5)
        self.slider_label = ctk.CTkLabel(options_frame, text="2.5", font=("Arial", 14))
        self.slider_label.grid(row=1, column=5, padx=10, pady=5)

        # Group weights
        weights_frame = ctk.CTkFrame(self)
        weights_frame.pack(pady=10, padx=10, fill="x")
        self.build_weight_slider(weights_frame)

        button = ctk.CTkButton(self, text="Search", command=self.on_button_click)
        button.pack(pady=10)

    def build_weight_slider(self, parent):
        CRITERIA = ["price", "duration", "transfers", "time-convenience", "flexibility"]
        self.sliders = {}
        self.slider_labels = {}
        weight_label = ctk.CTkLabel(parent, text="Weighted ranking", font=("Arial", 14, "bold"))
        weight_label.grid(row=0, column=0, padx=10)

        for i, name in enumerate(CRITERIA):
            ctk.CTkLabel(parent, text=name.capitalize(), font=("Arial", 14)).grid(row=1, column=i, padx=10, pady=5, sticky="w")
            slider = ctk.CTkSlider(parent, from_=0, to=100, number_of_steps=20, width=120, command=self.on_weights_slider_change)
            slider.set(20)
            slider.grid(row=2, column=i, padx=10, pady=5)

            label = ctk.CTkLabel(parent, text="20%", font=("Arial", 14), width=40)
            label.grid(row=3, column=i, padx=10, pady=5)
            
            self.sliders[name] = slider
            self.slider_labels[name] = label

    def get_weights(self):
        raw = {k: s.get() for k, s in self.sliders.items()}
        total = sum(raw.values())
        if total == 0:
            return {k: 1 / len(raw) for k in raw}
        return {k: v / total for k, v in raw.items()}
    
    def on_button_click(self):
        error_message = validate_search_query(self.departure_entry.get(), self.budget_entry.get(), self.transfers_entry.get(), self.changeability_checkbox.get(), self.refundability_checkbox.get(), self.slider.get())
        
        if error_message is not None:
            self.open_error_window(error_message)
        else:
            departure_date = datetime.strptime(self.departure_entry.get(), "%Y-%m-%d").date()
            bid: Bid = Bid(departure_date, self.departure_time.get(), self.departure_city.get(), self.arrival_city.get(), self.budget_entry.get(), self.transfers_entry.get(), self.changeability_checkbox.get(), self.refundability_checkbox.get(), self.slider.get())
            self.search_offers(bid)

    def open_error_window(self, e):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error!")
        error_window.geometry("300x150")       

        error_message = ctk.CTkLabel(error_window, text=e, font=("Arial", 12), text_color="red", wraplength=260)
        error_message.pack(pady=10)

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

    def on_weights_slider_change(self, _value):
        weights = self.get_weights()
        for k,w in weights.items():
            self.slider_labels[k].configure(text=f"{w * 100:.0f}%")
    
    def search_offers(self, bid):
        print("Searching for offers with the following criteria:")
        print(bid.changeable, bid.refundable)
        # open new window with search results
        travel_date = bid.departure_date
        travel_dates = [travel_date, travel_date + timedelta(days=1)]  # Add the departure date to the list
        generate_offers(travel_dates)
        self.open_results_window(bid)
    
    def open_results_window(self, bid):
        results_window = ctk.CTkToplevel(self)
        results_window.title("Search Results")
        results_window.geometry("1100x1000")

        label = ctk.CTkLabel(results_window, text="Search Results", font=("Arial", 16))
        label.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(results_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        filtered_offers = filter_relevant_offers(self.get_all_offers(), bid)
        print(f"Found {len(filtered_offers)} relevant offers.")
        weights = self.get_weights()
        ranked_offers = rank_relevant_offers(filtered_offers, bid, weights)
        cheapest_offer_id = get_cheapest_route(ranked_offers).offer_id
        shortest_offer_id = get_shortest_route(ranked_offers).offer_id
        best_rated_offer_id = get_best_rated_route(ranked_offers).offer_id
        for i, o in enumerate(ranked_offers):
            offer_frame = ctk.CTkFrame(scroll_frame, fg_color="gray20")
            offer_frame.pack(pady=15, padx=10, fill="x")
            destination_label = ctk.CTkLabel(offer_frame, text=f"{o.company}: Madrid - {o.destination}", font=("Arial", 16, "bold"))
            destination_label.grid(row=0, column=0, padx=10, sticky="w")
            if o.offer_id == cheapest_offer_id:
                cheap_label = ctk.CTkLabel(offer_frame, text="CHEAPEST ROUTE", text_color=color, font=("Arial", 12))
                cheap_label.grid(row=0, column=1, padx=10, sticky="w")
            if o.offer_id == shortest_offer_id:
                cheap_label = ctk.CTkLabel(offer_frame, text="FASTEST ROUTE", text_color=color, font=("Arial", 12))
                cheap_label.grid(row=0, column=1, padx=10, sticky="w")
            if o.offer_id == best_rated_offer_id:
                cheap_label = ctk.CTkLabel(offer_frame, text="BEST CUSTOMER RATING", text_color=color, font=("Arial", 12))
                cheap_label.grid(row=0, column=1, padx=10, sticky="w")
            dep_label = ctk.CTkLabel(offer_frame, text=f"Departure: {o.travel_date} {o.departure_time.strftime('%H:%M')}", font=("Arial", 14))
            dep_label.grid(row=1, column=0, padx=10, sticky="w")
            arr_label = ctk.CTkLabel(offer_frame, text=f"Arrival: {o.arrival_date} {o.arrival_time.strftime('%H:%M')}", font=("Arial", 14))
            arr_label.grid(row=1, column=1, padx=10, sticky="w")
            duration_label = ctk.CTkLabel(offer_frame, text=f"Duration: {o.journey.minutes_to_hours()}", font=("Arial", 14)) 
            duration_label.grid(row=1, column=2, padx=10, sticky="w")
            # Select button
            choose_button = ctk.CTkButton(offer_frame, text="Choose offer", command=lambda offer=o: self.choose_option_click(offer)) 
            choose_button.grid(row=1, column=4, padx=10, sticky="w")

            price_label = ctk.CTkLabel(offer_frame, text=f"Price: €{o.price}", font=("Arial", 14, "italic"))
            price_label.grid(row=2, column=0, padx=10, sticky="w")
            transfers_label = ctk.CTkLabel(offer_frame, text=f"Transfers: {o.transfers}", font=("Arial", 14))
            transfers_label.grid(row=2, column=1, padx=10, sticky="w")
            rating_label = ctk.CTkLabel(offer_frame, text=f"Customer Rating: {o.customer_rating}/5", font=("Arial", 14))
            rating_label.grid(row=2, column=2, padx=10, sticky="w")
            luggage_label = ctk.CTkLabel(offer_frame, text=f"Luggage allowed: {o.luggage_allowance}kg", font=("Arial", 14))
            luggage_label.grid(row=3, column=0, padx=10, sticky="w")
            change_label = ctk.CTkLabel(offer_frame, text=f"Changeable: Yes" if o.changeability else "Changeable: No", font=("Arial", 14))
            change_label.grid(row=3, column=1, padx=10, sticky="w")
            refund_label = ctk.CTkLabel(offer_frame, text=f"Refundable: Yes" if o.refundability else "Refundable: No", font=("Arial", 14))
            refund_label.grid(row=3, column=2, padx=10, sticky="w")
            avail_seats_label = ctk.CTkLabel(offer_frame, text=f"Available seats: {o.available_seats}", font=("Arial", 14))
            avail_seats_label.grid(row=3, column=3, padx=10, sticky="w")
            env_meas_label = ctk.CTkLabel(offer_frame, text=f"Environmental measure: {o.environmental_measure}", font=("Arial", 14))
            env_meas_label.grid(row=3, column=4, padx=10, sticky="w")

            ranked_frame = ctk.CTkFrame(offer_frame, fg_color=color)
            ranked_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=(5,10), sticky="ew")

            ranked_label = ctk.CTkLabel(ranked_frame, text="Ranking scores", font=("Arial", 14, "bold"))
            ranked_label.grid(row=0, column=0, padx=10, sticky="w")
            t_score_label = ctk.CTkLabel(ranked_frame, text=f"Total score: {o.ranking['total_score']}", font=("Arial", 14))
            t_score_label.grid(row=1, column=0, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text="Weighted: ", font=("Arial", 12))
            weight_label.grid(row=2, column=0, padx=10, sticky="w")
            p_score_label = ctk.CTkLabel(ranked_frame, text=f"Price score: {o.ranking['price_score']:.2f}", font=("Arial", 14))
            p_score_label.grid(row=1, column=1, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text=f"{weights['price']:.2f}/1.0", font=("Arial", 12))
            weight_label.grid(row=2, column=1, padx=10, sticky="w")
            d_score_label = ctk.CTkLabel(ranked_frame, text=f"Duration score: {o.ranking['duration_score']:.2f}", font=("Arial", 14))
            d_score_label.grid(row=1, column=2, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text=f"{weights['duration']:.2f}/1.0", font=("Arial", 12))
            weight_label.grid(row=2, column=2, padx=10, sticky="w")
            tr_score_label = ctk.CTkLabel(ranked_frame, text=f"Transfer score: {o.ranking['transfer_score']:.2f}", font=("Arial", 14))
            tr_score_label.grid(row=1, column=3, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text=f"{weights['transfers']:.2f}/1.0", font=("Arial", 12))
            weight_label.grid(row=2, column=3, padx=10, sticky="w")
            ti_score_label = ctk.CTkLabel(ranked_frame, text=f"Time-convenience score: {o.ranking['time_score']:.2f}", font=("Arial", 14))
            ti_score_label.grid(row=1, column=4, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text=f"{weights['time-convenience']:.2f}/1.0", font=("Arial", 12))
            weight_label.grid(row=2, column=4, padx=10, sticky="w")
            f_score_label = ctk.CTkLabel(ranked_frame, text=f"Flexibility score: {o.ranking['flex_score']:.2f}", font=("Arial", 14))
            f_score_label.grid(row=1, column=5, padx=10, sticky="w")
            weight_label = ctk.CTkLabel(ranked_frame, text=f"{weights['flexibility']:.2f}/1.0", font=("Arial", 12))
            weight_label.grid(row=2, column=5, padx=10, sticky="w")
            #print(f"Ranked offers: {o.offer_id} {o.company} to {o.destination} with price {o.price} and rating {o.customer_rating}")
            if i == 0:
                explanation_label = ctk.CTkLabel(offer_frame, text=f"{self.get_explanation(o)}", font=("Arial", 12, "italic"), wraplength=1000)
                explanation_label.grid(row=5, column=0, columnspan=5, padx=10, pady=5, sticky="w")

    def get_explanation(self, o):
        strengths, weaknesses = [], []
        r = o.ranking
        print("Explain this:", o.ranking)
        if r['price_score'] >= 0.7:
            strengths.append(f"a low price of €{o.price:.2f}")
        elif r['price_score'] <= 0.3:
            weaknesses.append(f"a higher price of €{o.price:.2f}")

        if r['duration_score'] >= 0.7:
            strengths.append(f"short duration of {o.journey.minutes_to_hours()}")
        elif r['duration_score'] <= 0.3:
            weaknesses.append(f"long duration of {o.journey.minutes_to_hours()}")

        if r['transfer_score'] >= 0.7:
            strengths.append(f"few transfers ({o.transfers})")
        elif r['transfer_score'] <= 0.3:
            weaknesses.append(f"many transfers ({o.transfers})")
        
        if r['time_score'] == 1.0:
            strengths.append(f"a departure that fits the preferred time ({o.departure_time})")
        elif r['time_score'] <= 0.6:
            weaknesses.append(f"a departure outside the preferred time ({o.departure_time})")

        if r['flex_score'] == 1.0:
            strengths.append(f"a highly flexible fare")
        elif r['flex_score'] == 0.0:
            weaknesses.append(f"an inflexible fare")

        text = "Ranked highest under the selected weights"
        if strengths:
            text += f" because it offers {self.join_list(strengths)}"
            if len(weaknesses) == 0:
                text += ", and zero weaknesses"
        if weaknesses:
            text += f" although it has {self.join_list(weaknesses)}"
        return text + "."

    def join_list(self, items):
        if len(items) <= 1:
            return "".join(items)
        return ", ".join(items[:-1]) + " and " + items[-1]

    def get_all_offers(self) -> Offer:
        with open('bus_bidder/data/offers.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.offers = []
            for row in reader:
                journey = Journey(row['destination'], row['travel_date'], row['departure_time'], row['arrival_time'], row['arrival_date'], row['duration'], row['transfers'], row['environmental_measure'])
                offer = Offer(row['offer_id'], row['company'], journey, row['price'], row['luggage_allowance'], row['changeability'], row['refundability'], row['available_seats'], row['customer_rating'], {})
                self.offers.append(offer) 
            return self.offers
    
    def choose_option_click(self, offer):
        print(f"Chose offer {offer.offer_id} departing at {offer.departure_time}")
        self.open_traveller_info_window(offer)

    def open_traveller_info_window(self, offer):
        t_info_window = ctk.CTkToplevel(self)
        t_info_window.title("Confirm booking")
        t_info_window.geometry("800x800")

        confirm_label = ctk.CTkLabel(t_info_window, text="Would you like to confirm this offer?", font=("Arial", 14))
        confirm_label.pack(pady=10)
        label = ctk.CTkLabel(t_info_window, text=f"{offer}", font=("Arial", 12), wraplength=760)
        label.pack(pady=10)

        traveller_frame = ctk.CTkFrame(t_info_window)
        traveller_frame.pack(fill="both", expand=True, padx=10, pady=10)

        traveller_label = ctk.CTkLabel(traveller_frame, text="Personal info", font=("Arial", 16))
        traveller_label.grid(row=0, column=0, padx=10, sticky="w")
        name_label = ctk.CTkLabel(traveller_frame, text="Name", font=("Arial", 14))
        name_label.grid(row=1, column=0, padx=10, sticky="w")
        email_label = ctk.CTkLabel(traveller_frame, text="Email", font=("Arial", 14))
        email_label.grid(row=1, column=1, padx=10, sticky="w")
        phone_label = ctk.CTkLabel(traveller_frame, text="Phone number", font=("Arial", 14))
        phone_label.grid(row=1, column=2, padx=10, sticky="w")

        self.name_entry = ctk.CTkEntry(traveller_frame, placeholder_text="Enter your name...", width=200)
        self.name_entry.grid(row=2, column=0, padx=10, sticky="w")
        self.email_entry = ctk.CTkEntry(traveller_frame, placeholder_text="Enter your email...", width=200)
        self.email_entry.grid(row=2, column=1, padx=10, sticky="w")
        self.phone_entry = ctk.CTkEntry(traveller_frame, placeholder_text="Enter your phone number...", width=200)
        self.phone_entry.grid(row=2, column=2, padx=10, sticky="w")

        booking_label = ctk.CTkLabel(traveller_frame, text=f"Seats available: {offer.available_seats}", font=("Arial", 14))
        booking_label.grid(row=3, column=0, padx=10, sticky="w")
        self.booking_entry = ctk.CTkEntry(traveller_frame, placeholder_text="How many seats do you want?", width=300)
        self.booking_entry.grid(row=4, column=0, padx=10, sticky="w")

        confirm_button = ctk.CTkButton(traveller_frame, text="Confirm offer", command=lambda: self.confirm_booking_click(offer))
        confirm_button.grid(row=4, column=2, padx=10, sticky="w")

    def confirm_booking_click(self, offer):
        booking_reference =f"0B{uuid.uuid4().hex[:8].upper()}" #Unique booking ID
        name_entry = self.name_entry.get()
        email_entry = self.email_entry.get()
        phone_entry = self.phone_entry.get()
        seats = self.booking_entry.get()
        error_message = validate_confirmation_query(booking_reference, name_entry, email_entry, phone_entry, seats, offer.available_seats)

        if error_message is not None:
            self.open_error_window(error_message)
        else:
            traveller: Traveller = Traveller(name_entry, email_entry, phone_entry)
            booking: Booking = Booking(booking_reference, traveller, offer, self.booking_entry.get())
            write_booking(booking)
            self.confirm_booking_window(booking)

    def confirm_booking_window(self, booking):
        confirmed_window = ctk.CTkToplevel(self)
        confirmed_window.geometry("550x100")
        confirmed_window.title("Booking confirmed!")

        confirmed_label = ctk.CTkLabel(confirmed_window, text=f"Booking: {booking.booking_reference} is confirmed for traveller {booking.traveller.name}.", font=("Arial", 14))
        confirmed_label.pack(pady=10, padx=10)


if __name__ == "__main__":
    app = BusBidderApp()
    app.mainloop()