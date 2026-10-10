import os
import time
import urllib.request
from pathlib import Path


class AmtrakGtfsParser:
    # Official or open-source Amtrak GTFS producer URL endpoint
    AMTRAK_GTFS_URL = "https://piemadd.com"

    def __init__(self, base_dir=None):
        # Establish file structure mapping back to AmtrakTrainRoutesApp/data/
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent
        else:
            self.base_dir = Path(base_dir)

        self.data_dir = self.base_dir / "data"
        self.zip_path = self.data_dir / "amtrak-gtfs.zip"

    def ensure_fresh_gtfs(self) -> bool:
        """
        Validates the existence and age of the locally cached ZIP archive.
        Fetches a fresh copy if missing or older than 24 hours (86,400 seconds).
        Returns True if a download occurred, False otherwise.
        """
        # Ensure the target data folder physically exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        now = time.time()
        one_day_seconds = 86400

        # Check if download is required
        if not self.zip_path.exists():
            print("Local 'amtrak-gtfs.zip' not found. Initiating baseline download...")
            self._download_gtfs_archive()
            return True

        file_age = now - self.zip_path.stat().st_mtime
        if file_age > one_day_seconds:
            print(f"Cache expired! File is {file_age / 3600:.1f} hours old. Syncing fresh GTFS stream...")
            self._download_gtfs_archive()
            return True

        print(f"Cache valid. Local GTFS archive is only {file_age / 3600:.1f} hours old. Skipping network request.")
        return False

    def _download_gtfs_archive(self):
        """Streams raw chunk binaries out of the transit feed URL straight onto disk."""
        print(f"Fetching stream from: {self.AMTRAK_GTFS_URL}")
        try:
            # Custom User-Agent header prevents some host firewalls from rejecting python-urllib streams
            req = urllib.request.Request(
                self.AMTRAK_GTFS_URL,
                headers={'User-Agent': 'Mozilla/5.0 (Ubuntu; Linux x86_64) AmtrakTrainRoutesApp/1.0'}
            )

            with urllib.request.urlopen(req) as response, open(self.zip_path, 'wb') as out_file:
                chunk_size = 1024 * 64  # 64kb chunks
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
            print(f" Successfully saved fresh archive to: {self.zip_path}")
        except Exception as e:
            print(f" Error encountered during streaming download: {e}")
            raise e

# import csv
# import io
# import os
# import time
# import zipfile
# import urllib.request
# from collections import defaultdict
# import networkx as nx
#
#
# class AmtrakGTFSParser:
#     # Official producer URL discovered via MobilityDatabase
#     GTFS_URL = "https://content.amtrak.com/content/gtfs/GTFS.zip"
#
#     def __init__(self, zip_path: str):
#         self.zip_path = zip_path
#         self.graph = nx.DiGraph()
#         self.route_id_to_name = {}
#         self.trip_id_to_route = {}
#         self.station_names = {}
#
#     def ensure_fresh_data(self):
#         """
#         Validates the state of the local file.
#         Downloads from Amtrak's official servers if missing or older than 24 hours.
#         """
#         os.makedirs(os.path.dirname(self.zip_path), exist_ok=True)
#
#         should_download = False
#         if not os.path.exists(self.zip_path):
#             print("Local GTFS archive not found. Initiating initial dataset download...")
#             should_download = True
#         else:
#             # Check file age to strictly limit queries to max once per day
#             file_age_seconds = time.time() - os.path.getmtime(self.zip_path)
#             if file_age_seconds > 86400:  # 24 hours
#                 print("Local GTFS data is older than 24 hours. Fetching daily update...")
#                 should_download = True
#
#         if should_download:
#             try:
#                 headers = {'User-Agent': 'Mozilla/5.0 (Ubuntu; Linux x86_64) AmtrakRouter/1.0'}
#                 req = urllib.request.Request(self.GTFS_URL, headers=headers)
#
#                 with urllib.request.urlopen(req) as response, open(self.zip_path, 'wb') as out_file:
#                     out_file.write(response.read())
#                 print("Successfully updated Amtrak GTFS archive from official producer endpoints.")
#             except Exception as e:
#                 print(f"Network sync failed ({e}). Proceeding using historical cache if available.")
#
#     def _open_csv_from_zip(self, zf: zipfile.ZipFile, filename: str):
#         try:
#             content = zf.read(filename).decode('utf-8-sig')
#             return csv.DictReader(io.StringIO(content))
#         except KeyError:
#             raise FileNotFoundError(f"Required file {filename} missing from GTFS zip.")
#
#     def parse_and_build(self):
#         """Downloads/verifies files and builds the NetworkX train topology."""
#         self.ensure_fresh_data()
#
#         if not os.path.exists(self.zip_path):
#             print("Initialization failed: No valid dataset source targets available.")
#             return
#
#         with zipfile.ZipFile(self.zip_path, 'r') as zf:
#             # 1. Parse Stations
#             for row in self._open_csv_from_zip(zf, 'stops.txt'):
#                 stop_id = row['stop_id']
#                 self.station_names[stop_id] = row['stop_name']
#                 self.graph.add_node(stop_id, name=row['stop_name'])
#
#             # 2. Parse Named Trains
#             for row in self._open_csv_from_zip(zf, 'routes.txt'):
#                 name = row.get('route_long_name') or row.get('route_short_name')
#                 self.route_id_to_name[row['route_id']] = name
#
#             # 3. Parse Trips
#             for row in self._open_csv_from_zip(zf, 'trips.txt'):
#                 trip_id = row['trip_id']
#                 route_id = row['route_id']
#                 train_num = row.get('trip_short_name') or "Unknown"
#
#                 self.trip_id_to_route[trip_id] = {
#                     "route_name": self.route_id_to_name.get(route_id, "Amtrak Route"),
#                     "train_number": train_num
#                 }
#
#             # 4. Connect Physical Layout Sequences
#             trip_sequences = defaultdict(list)
#             for row in self._open_csv_from_zip(zf, 'stop_times.txt'):
#                 trip_sequences[row['trip_id']].append({
#                     'stop_id': row['stop_id'],
#                     'sequence': int(row['stop_sequence']),
#                     'arrival': row['arrival_time'],
#                     'departure': row['departure_time']
#                 })
#
#             for trip_id, stops in trip_sequences.items():
#                 stops.sort(key=lambda x: x['sequence'])
#                 trip_info = self.trip_id_to_route.get(trip_id)
#                 if not trip_info:
#                     continue
#
#                 for i in range(len(stops) - 1):
#                     u = stops[i]['stop_id']
#                     v = stops[i + 1]['stop_id']
#
#                     if not self.graph.has_edge(u, v):
#                         self.graph.add_edge(u, v, services=defaultdict(set))
#
#                     service_key = (trip_info['route_name'], trip_info['train_number'])
#                     self.graph[u][v]['services'][service_key].add(stops[i]['departure'])
#
#         print(f"Loaded network topology graph: {len(self.graph.nodes)} stations, {len(self.graph.edges)} connections.")
#
#     def query_train_options(self, origin: str, destination: str):
#         origin, destination = origin.upper(), destination.upper()
#         if origin not in self.graph or destination not in self.graph:
#             return None
#
#         try:
#             paths = list(nx.all_simple_paths(self.graph, source=origin, target=destination, cutoff=3))
#             compiled_itineraries = []
#
#             for path in paths:
#                 itinerary_segments = []
#                 for i in range(len(path) - 1):
#                     u, v = path[i], path[i + 1]
#                     edge_data = self.graph[u][v]
#
#                     available_trains = []
#                     for (route, num), times in edge_data['services'].items():
#                         available_trains.append({
#                             "train_name": route,
#                             "train_number": num,
#                             "sample_departures": sorted(list(times))[:2]
#                         })
#
#                     itinerary_segments.append({"from": u, "to": v, "trains": available_trains})
#
#                 compiled_itineraries.append({"station_sequence": path, "segments": itinerary_segments})
#             return compiled_itineraries
#         except nx.NetworkXNoPath:
#             return []
