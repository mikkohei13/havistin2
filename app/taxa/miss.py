# Page that shows which species are missing from the given location. User gives a location (lat, lon) and taxon.

from helpers import common_helpers
import datetime

def validate_lat(lat_untrusted):
    lat = float(lat_untrusted)
    if lat < 0:
        raise ValueError("Latitude should be positive")
    return lat

def validate_lon(lon_untrusted):
    lon = float(lon_untrusted)
    if lon < 0:
        raise ValueError("Longitude should be positive")
    return lon

def validate_year(year_untrusted):
    current_year = datetime.datetime.now().year
    year = int(year_untrusted)
    if year < 1900 or year > current_year:
        raise ValueError("Year should be between 1900 and current year")
    return year

def main(lat_untrusted, lon_untrusted, taxon_untrusted, year_untrusted):

    # Validate inputs
    # Lat and lon should be positive decimal numbers
    lat = validate_lat(lat_untrusted)
    lon = validate_lon(lon_untrusted)

    # Taxon should be format "MX.{integer}"
    qname = common_helpers.valid_qname(taxon_untrusted)

    # Year should be between 1900 and current year
    year = validate_year(year_untrusted)

    html = dict()
    html["lat"] = lat
    html["lon"] = lon
    html["qname"] = qname
    html["year"] = year

    return html
