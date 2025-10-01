

from helpers import common_helpers

def species_list(date_filter, taxon_id):
    date_filter = date_filter.replace("/", "%2F")

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesScientificName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=1000&page=1&cache=true&taxonId={ taxon_id }&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&time={ date_filter }&collectionIdNot=HR.48%2CHR.3671%2CHR.2029&access_token="
    data = common_helpers.fetch_finbif_api(url)
#    print(data)

    species_counts = dict()
    count_sum = 0

    for item in data["results"]:
        species = item["aggregateBy"]["unit.linkings.originalTaxon.speciesScientificName"]
        count = item["count"]
        species_counts[species] = count
        count_sum = count_sum + count

    return species_counts, count_sum


def make_change_html(all_species):
    min_count = 1
    
    html = "<table class='styled-table'>\n"
    html += "<thead>\n<tr>"
    html += "<th>Laji</th>"
    html += "<th>Vuotta aiemmin</th>"
    html += "<th>Viimeiset 30 pv</th>"
    html += "<th>Normalisoitu suhde</th>"
    html += "<th>&nbsp;</th>"
    html += "</tr>\n</thead>\n"
    html += "<tbody>\n"

    for species, data in all_species.items():
        if data['count'] < min_count:
            continue

        bar_width = int(data['proportion'] * 20)
        css_class = ""

        if 10 == data['proportion']:
            data['proportion'] = "&gt;10"
            css_class = "capped"
        elif data['proportion'] >= 1:
            css_class = "positive"
        elif data['proportion'] < 1:
            css_class = "negative"

        html += "<tr>"
        html += f"<td>{ species }</td>"
        html += f"<td>{ data['count_last_year'] }</td>"
        html += f"<td>{ data['count'] }</td>"
        html += f"<td>{ data['proportion'] }</td>"
        html += f"<td><span class='proportion_bar { css_class }' style='width: { bar_width }px;'>&nbsp;</span></td>"
        html += "</tr>\n"
        
    html += "</thead>\n</table>\n"

    return html


def make_change_dict(species_this_year, sum_this_year, species_last_year, sum_last_year):
    proportion_cap = 10
    all_species = dict()

    for species, count in species_this_year.items():

        # Species observed on both years
        if species in species_last_year:
            count_normalized = count / sum_this_year
            count_last_year = species_last_year[species]
            count_last_year_normalized = count_last_year / sum_last_year
            proportion = round(count_normalized / count_last_year_normalized, 2)

            if proportion > proportion_cap:
                proportion = proportion_cap

        # Species observed only this year
        else:
            proportion = proportion_cap
            count_last_year = 0

        single_species = dict()
        single_species["count_last_year"] = count_last_year
        single_species["count"] = count
        single_species["proportion"] = proportion

        all_species[species] = single_species

        # Debug
#        print(f"{ species }: { count_normalized } / { count_last_year_normalized } = { proportion }")

    # Sort descending
    sorted_all_species = dict(sorted(all_species.items(), key=lambda x: x[1]['proportion'], reverse=True))

    return sorted_all_species


def main(taxon_id_untrusted):
    html = dict()

    taxon_id = common_helpers.valid_qname(taxon_id_untrusted)

    species_this_year, sum_this_year = species_list("-31/-1", taxon_id)
    species_last_year, sum_last_year = species_list("-396/-366", taxon_id)

    all_species = make_change_dict(species_this_year, sum_this_year, species_last_year, sum_last_year)

    html["data"] = make_change_html(all_species)

    return html
