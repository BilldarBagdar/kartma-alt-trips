import os
import datetime
from GtfsParser import AmtrakGtfsParser
from AmtrakTicketingHandoff import generate_amtrak_deeplink

class Main:

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        zip_target = os.path.join(base_dir, "data", "amtrak-gtfs.zip")

        print("Initializing train-centric routing engine...")
        self.engine = AmtrakGtfsParser(zip_target)
        self.engine.parse_and_build()
        self.options = []
        self._origin_stn = ""
        self._dest_stn = ""
        self._start_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%m/%d/%Y")
        self._adult_count = 1
        
    @property
    def origin_station(self):
        return self._origin_stn
    @origin_station.setter
    def origin_station(self, stn):
        self._origin_stn = stn

    @property
    def dest_station(self):
        return self._dest_stn
    @dest_station.setter
    def dest_station(self, stn):
        self._dest_stn = stn

    @property
    def departure_date(self):
        return self._start_date
    @departure_date.setter
    def departure_date(self, dt):
        self._start_date = dt

    @property
    def travelling_adults(self):
        return self._adult_count
    @travelling_adults.setter
    def travelling_adults(self, dt):
        self._adult_count = dt

    def generate_parameterized_url_string(self):
        print(f"\nSearching for all valid physical rail tracks from {self.origin_station} -> {self.dest_station}:")
        self.options = self.engine.query_train_options(self.origin_station, self.dest_station)

        if self.options:
            for idx, opt in enumerate(self.options[:3], 1):
                print(f"Option #{idx}: Track Sequence: {' -> '.join(opt['station_sequence'])}")

            # Leveraging the parameter flexibility (e.g., booking for 2 adults next month)
            url = generate_amtrak_deeplink(
                origin=self.origin_station,
                destination=self.dest_station,
                travel_date=self.departure_date,
                adults=self.travelling_adults
            )
            print(f"\nGenerated Amtrak Booking Desk Deep Link:\n{url}")
        else:
            print("No pure physical rail routes detected between those station codes.")


if __name__ == "__main__":
    # Boot the application state engine
    app = Main()

    # Configure your active search parameters via properties
    app.origin_station = "SEA"
    app.dest_station = "PDX"
    app.departure_date = "11/15/2026"
    app.travelling_adults = 2

    # Execute routing pipeline and deep-link emission
    app.generate_parameterized_url_string()
