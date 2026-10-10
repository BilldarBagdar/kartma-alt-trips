import unittest
import os
import zipfile
import shutil
import urllib.parse
from main import Main


class TestAmtrakMainInterface(unittest.TestCase):
    def setUp(self):
        # Anchor the environment to an isolated workspace
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_data_dir = os.path.join(self.base_dir, "data")
        self.test_zip_path = os.path.join(self.test_data_dir, "amtrak-gtfs.zip")

        # Build out a predictable, minimal track layout inside the active target folder
        os.makedirs(self.test_data_dir, exist_ok=True)

        stops_txt = "stop_id,stop_name\nNYP,New York\nPHL,Philadelphia\nWAS,Washington\n"
        routes_txt = "route_id,route_long_name\nNE,Northeast Regional\n"
        trips_txt = "trip_id,route_id,trip_short_name\ntrip88,NE,188\n"
        stop_times_txt = ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                          "trip88,08:00:00,08:00:00,NYP,1\n"
                          "trip88,09:15:00,09:15:00,PHL,2\n"
                          "trip88,11:30:00,11:30:00,WAS,3\n")

        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            zf.writestr('stops.txt', stops_txt)
            zf.writestr('routes.txt', routes_txt)
            zf.writestr('trips.txt', trips_txt)
            zf.writestr('stop_times.txt', stop_times_txt)

    def tearDown(self):
        # Remove testing data fixtures
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_main_class_state_and_link_generation(self):
        """Verifies that Main state parameters are properly set and bound to the deep-link exporter."""
        # 1. Initialize the Main engine state layer
        app = Main()

        # 2. Assert property defaults behave as expected
        self.assertEqual(app.options, [])
        self.assertEqual(app.travelling_adults, 1)

        # 3. Apply state definitions through your custom setters
        app.origin_station = "NYP"
        app.dest_station = "WAS"
        app.departure_date = "12/25/2026"
        app.travelling_adults = 3

        # 4. Capture the console or execution path outcomes
        app.generate_parameterized_url_string()

        # 5. Assert options array populated successfully based on real tracks
        self.assertGreater(len(app.options), 0, "Main engine failed to resolve valid rail paths.")
        self.assertEqual(app.options[0]['station_sequence'], ["NYP", "PHL", "WAS"])

        # 6. Re-verify explicit route construction outputs indirectly
        from AmtrakTicketingHandoff import generate_amtrak_deeplink
        generated_url = generate_amtrak_deeplink(
            origin=app.origin_station,
            destination=app.dest_station,
            travel_date=app.departure_date,
            adults=app.travelling_adults
        )

        # Parse output URL segments safely to ensure format compliance
        parsed_url = urllib.parse.urlparse(generated_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        self.assertEqual(query_params['origin'][0], "NYP")
        self.assertEqual(query_params['destination'][0], "WAS")
        self.assertEqual(query_params['outboundDate'][0], "12/25/2026")
        self.assertEqual(query_params['adults'][0], "3")


if __name__ == '__main__':
    unittest.main()
