# Page that shows which species are missing from the given location. User gives a location (lat, lon) and taxon.

from helpers import common_helpers
import datetime
import math

# Input validation functions
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


# Calculate bounding box for the given lat, lon and box size in kilometers
def bounding_box(lat, lon, box_size):
    # Earth radius in km
    R = 6371.0

    # Convert lat and lon to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate the angular distance in radians on the sphere from the center of the map
    angular_distance = box_size / R

    # Calculate the min and max latitudes
    lat_min = lat - math.degrees(angular_distance)
    lat_max = lat + math.degrees(angular_distance)

    # Calculate the min and max longitudes
    delta_lon = math.degrees(angular_distance / math.cos(lat_rad))
    lon_min = lon - delta_lon
    lon_max = lon + delta_lon

    return round(lat_min, 4), round(lat_max, 4), round(lon_min, 4), round(lon_max, 4)


# Function to get observation data from the given area
def get_observation_counts(qname, lat, lon, year_begin):
    lat_min, lat_max, lon_min, lon_max = bounding_box(lat, lon, 100)
    return lat_min, lat_max, lon_min, lon_max

#    species_data = common_helpers.fetch_finbif_api(f"")


def main(lat_untrusted, lon_untrusted, taxon_untrusted, year_untrusted):

    # Validate inputs
    # Lat and lon should be positive decimal numbers
    lat = validate_lat(lat_untrusted)
    lon = validate_lon(lon_untrusted)

    # Taxon should be format "MX.{integer}"
    qname = common_helpers.valid_qname(taxon_untrusted)

    # Year should be between 1900 and current year
    year = validate_year(year_untrusted)

    lat_min, lat_max, lon_min, lon_max = get_observation_counts(qname, lat, lon, year)

    html = dict()
    html["bbox"] = f"{lat_min}:{lat_max}:{lon_min}:{lon_max}"

    html["lat"] = lat
    html["lon"] = lon
    html["qname"] = qname
    html["year"] = year

    return html
