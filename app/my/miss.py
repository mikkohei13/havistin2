# Page that shows which species are missing from the given location. User gives a location (lat, lon) and taxon.

from helpers import common_helpers
import datetime
import math

# Input validation functions
def validate_lat(lat_untrusted):
    lat = float(lat_untrusted)
    if lat < 0:
        raise ValueError("Latitude should be positive")
    return round(lat, 4)


def validate_lon(lon_untrusted):
    lon = float(lon_untrusted)
    if lon < 0:
        raise ValueError("Longitude should be positive")
    return round(lon, 4)


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
def get_observation_counts(qname, lat, lon, year_begin, radius):
    lat_min, lat_max, lon_min, lon_max = bounding_box(lat, lon, radius)

    # bbox should be format 59.1007%3A60.8993%3A22.2014%3A25.7986%3AWGS84%3A1
    bbox = f"{lat_min}%3A{lat_max}%3A{lon_min}%3A{lon_max}%3AWGS84%3A1"

    # time is "year_begin/year_current"
    time = f"{year_begin}/{datetime.datetime.now().year}"

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.taxon.id%2Cunit.linkings.taxon.nameFinnish%2Cunit.linkings.taxon.scientificName&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=1000&page=1&cache=true&taxonId={ qname }&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&taxonRankId=MX.species&countryId=ML.206&time={ time }&individualCountMin=1&coordinates={ bbox }&qualityIssues=NO_ISSUES&access_token="

    species_data = common_helpers.fetch_finbif_api(url)

    # Loop species and make a dict with species names and counts
    species_dict = dict()
    for species in species_data["results"]:

        single_species_dict = dict()
        single_species_dict["count"] = species["count"]
        single_species_dict["fi"] = species["aggregateBy"]["unit.linkings.taxon.nameFinnish"]
        single_species_dict["sci"] = species["aggregateBy"]["unit.linkings.taxon.scientificName"]

        species_dict[species["aggregateBy"]["unit.linkings.taxon.id"]] = single_species_dict

    return species_dict
# Compare two species_dicts and return species that are in the first dict but not in the second
def compare_species_dicts(species_dict_far, species_dict_near):
    missing_species = dict()
    for key, value in species_dict_far.items():
        if key not in species_dict_near:
            missing_species[key] = value

    return missing_species


def generate_table_html(species_dict):
    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Nimi</th><th>Tieteellinen</th><th>Havaintoja</th></tr></thead>\n<tbody>\n"
    for key, value in species_dict.items():
        html += "<tr>"
        html += f"<td><a href='{ key }'>{ value['fi'] }</a></td>"
        html += f"<td><em>{ value['sci'] }</em></td>"
        html += f"<td>{ value['count'] }</td>"
        html += "</tr>\n"
    html += "</tbody>\n</table>"
    return html


def main(coord_untrusted):
    html = dict()

    return html
