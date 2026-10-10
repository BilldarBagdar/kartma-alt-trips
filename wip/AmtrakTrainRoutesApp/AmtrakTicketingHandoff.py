import urllib.parse
import datetime


def generate_amtrak_deeplink(origin: str, destination: str, travel_date: str = "", adults: int = 1) -> str:
    """
    Generates a checkout deep-link pointing to native web channels.

    :param (req) origin: 3-letter station code (e.g., 'SEA')
    :param (req) destination: 3-letter station code (e.g., 'PDX')
    :param (opt) travel_date: Target travel date string formatted as 'MM/DD/YYYY'.
                        Defaults to tomorrow if not specified.
    :param (opt) adults: Number of adult passengers. Defaults to 1.
    """
    base_url = "https://amtrak.com"

    # Fallback to tomorrow if the user hasn't provided a specific travel date
    if travel_date is None or len(travel_date) < 1:
        travel_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%m/%d/%Y")

    payload = {
        "wosid": "false",
        "origin": origin.upper(),
        "destination": destination.upper(),
        "outboundDate": travel_date,
        "adults": str(adults),
        "children": "0",
        "infants": "0",
        "seniors": "0",
        "military": "0",
        "railpass": "false"
    }

    return f"{base_url}?{urllib.parse.urlencode(payload)}"
