import json
import sys
from helpers import common_helpers

def read_atlas_species():
    """Load atlas-species.json and return as dictionary"""
    filename = "./data/atlas-species.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {filename} not found", file=sys.stdout)
        return {}

def get_observations(taxon_id):
    """
    Fetch all observation pages from FinBIF API for a given taxon.
    Returns list of observations: [{lat, lon, dayOfYear}, ...]
    """
    observations = []
    page = 1
    page_size = 10000  # Maximum per page
    
    while True:
        url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.dayOfYearBegin%2Cgathering.conversions.wgs84Grid01.lat%2Cgathering.conversions.wgs84Grid01.lon&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={page_size}&page={page}&cache=true&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time=2022%2F2025&timeAccuracy=7&individualCountMin=1&includeNullLoadDates=false&qualityIssues=NO_ISSUES&recordQuality=NEUTRAL&needsCheck=false&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="
        
        try:
            data_dict = common_helpers.fetch_finbif_api(url)
        except Exception as e:
            print(f"ERROR fetching observations for {taxon_id}: {str(e)}", file=sys.stdout)
            break
        
        # Check if we have results
        if 'results' not in data_dict or not data_dict['results']:
            break
        
        # Parse results - each result is an aggregate with keys for dayOfYearBegin, lat, lon
        for result in data_dict['results']:
            aggregate_by = result.get('aggregateBy', {})
            
            # Extract the aggregated values
            day_of_year = aggregate_by.get('gathering.conversions.dayOfYearBegin')
            lat = aggregate_by.get('gathering.conversions.wgs84Grid01.lat')
            lon = aggregate_by.get('gathering.conversions.wgs84Grid01.lon')
            
            # Only add if we have all required values
            if day_of_year is not None and lat is not None and lon is not None:
                try:
                    observations.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'dayOfYear': int(day_of_year)
                    })
                except (ValueError, TypeError):
                    # Skip invalid values
                    continue
        
        # Check if there are more pages
        total_results = data_dict.get('totalResults', 0)
        if page * page_size >= total_results:
            break
        
        page += 1
    
    return observations

def main(taxon_id=None):
    """Main function for rendering the page"""
    html = dict()
    
    # Load species data for dropdown
    species_dict = read_atlas_species()
    
    # Prepare species list for dropdown
    species_list = []
    for key, species in species_dict.items():
        species_list.append({
            'key': key,
            'fi': species.get('speciesFi', ''),
            'id': species.get('id', '').replace('http://tun.fi/', '')  # Remove prefix for cleaner IDs
        })
    
    # Sort by Finnish name
#    species_list.sort(key=lambda x: x['fi'])
    
    html['species_list'] = species_list
    html['default_taxon_id'] = taxon_id if taxon_id else ''
    
    return html

