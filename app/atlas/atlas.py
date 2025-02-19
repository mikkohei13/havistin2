

from datetime import timedelta, date
import json

import atlas.common_atlas as common_atlas
from helpers import common_helpers


def convert_collection_name(id):
    if "http://tun.fi/HR.4412" == id:
        return "Tiira"
    if  "http://tun.fi/HR.4471" == id:
        return "Vihko, lintuatlaslomake"
    if  "http://tun.fi/HR.1747" == id:
        return "Vihko, retkilomake"
    if  "http://tun.fi/HR.3211" == id:
        return "iNaturalist Suomi"
    if  "http://tun.fi/HR.157" == id:
        return "Maalintujen pistelaskennat"
    if  "http://tun.fi/HR.61" == id:
        return "Maalintujen linjalaskennat vakiolinjoilla"
    if  "http://tun.fi/HR.2691" == id:
        return "Maalintujen linjalaskennat ei-vakiolinjoilla"
    if  "http://tun.fi/HR.48" == id:
        return "Rengastus- ja löytörekisteri (TIPU)"
    if  "http://tun.fi/HR.4991" == id:
        return "Tiiran tulkitut atlashavainnot"
    if  "http://tun.fi/HR.4611" == id:
        return "FCG Finnish Consulting Group Oy:n lajihavainnot"
    if  "http://tun.fi/HR.4051" == id:
        return "LajiGIS: Lajin seurantakohteet: Petolinnut"
    if  "http://tun.fi/HR.64" == id:
        return "Lintujen pesäkorttiseuranta"
    if  "http://tun.fi/HR.95" == id:
        return "Sääksen pesäseuranta"
    if  "http://tun.fi/HR.49" == id:
        return "Petolintujen pesäseuranta"
    if  "http://tun.fi/HR.50" == id:
        return "Merikotkan pesäseuranta"
    if  "http://tun.fi/HR.5076" == id:
        return "Suomen Arvoluonto Oy luontoselvitysten havainnot"
    if  "http://tun.fi/HR.5795" == id:
        return "Luken aineistokooste 4. lintuatlakseen"
    if  "http://tun.fi/HR.5895 " == id:
        return "Oma riista -havainnot 4. lintuatlakseen"
    if  "http://tun.fi/HR.3992" == id:
        return "Vesilintulaskennat, Luken aineisto 2020-"
    if  "http://tun.fi/HR.3991" == id:
        return "Vesilintulaskennat, Luomuksen aineisto"
    if  "http://tun.fi/HR.62" == id:
        return "Vesilintulaskennat, luokittelematon aineisto"
    if  "http://tun.fi/HR.5895" == id:
        return "Oma riista -havainnot 4. lintuatlakseen"
    if  "http://tun.fi/HR.4731" == id:
        return "Metsähallituksen maalintujen linjalaskennat ei-vakiolinjoilla"
    if  "http://tun.fi/HR.5938" == id:
        return "Ylä-Lapin tunturialueiden riekkolaskenta"
    if  "http://tun.fi/HR.5775" == id:
        return "Ramboll Finland Oy:n lajihavainnot"
    if  "http://tun.fi/HR.2692" == id:
        return "Maalintujen laskennat - Aluekartoitukset"
    if  "http://tun.fi/HR.3691" == id:
        return "eBird"
    if  "http://tun.fi/HR.6098" == id:
        return "Lajitallennukset VARELY luonnonsuojeluyksikkö"
    return "Muu (" + id + ")"


def collections_data():
    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.collectionId&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    data_dict = common_helpers.fetch_finbif_api(api_url)

    total_obs_count = 0
    for i in data_dict["results"]:
        total_obs_count = total_obs_count + i["count"]

    collections_table = "<h3>Havaintolähteet</h3>"
    collections_table += "<table class='styled-table'>"
    collections_table += "<thead><tr><th>Tietolähde</th><th>Havaintoja</th><th>%</th></tr></thead>"
    collections_table += "<tbody>"

    for i in data_dict["results"]:
        collection_id = i["aggregateBy"]["document.collectionId"]
        collection_name = convert_collection_name(i["aggregateBy"]["document.collectionId"])

        collections_table += f"<tr><td><a href='{ collection_id }'>{ collection_name }</a></td>"
        collections_table += "<td>" + str(i["count"]) + "</td>"
        collections_table += "<td>" + str(round((i["count"] / total_obs_count) * 100, 2)) + " %</td></tr>"

    collections_table += f"<tr><td>Yhteensä</td><td>{total_obs_count}</td></tr>"
    collections_table += "</tbody></table>"

    return collections_table

'''
def breeding_data(atlas_class):

    if "D" == atlas_class:
        atlas_class = "MY.atlasClassEnumD"
    elif "C" == atlas_class:
        atlas_class = "MY.atlasClassEnumC"
    # TODO: exception for other cases

    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=20&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=" + atlas_class + "&access_token="

    data_dict = common_helpers.fetch_finbif_api(api_url)

    breeding_dict = dict()
    for item in data_dict["results"]:
        breeding_dict[item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]] = item["count"]

    return breeding_dict
'''


def daterange(start_date):
    end_date = date.today()

    # inclusive end
    day_count = int((end_date - start_date).days) + 1

    for n in range(day_count):
        yield start_date + timedelta(n)


def coordinate_accuracy_html(accuracy_dict, total_count):

    accuracy_table = "\n\n<h3>Havaintojen julkinen tarkkuus</h3>\n"
    accuracy_table += "<p>Mitä tarkempi havainnon paikka on, sitä paremmin sitä voidaan hyödyntää esim suojelutyössä. Tiirasta atlakseen tulee vain 10 km tasolle karkeistettuja havaintoja. Muista lähteistä arkaluontoiset sekä käyttäjien karkeistamat havainnot näkyvät tässä karkeistettuina, mutta suojelu- ym. käytössä ne ovat käytettävissä tarkkana.</p>\n"
    accuracy_table += "<table class='styled-table'>\n"
    accuracy_table += "<thead>\n<tr><th>Tarkkuus</th><th>Havaintoja</th><th>%</th><th> </th></tr>\n</thead>\n"
    accuracy_table += "<tbody>\n"

    percentage = round(accuracy_dict['1']/total_count*100, 1)
    accuracy_table += f"<tr><td>1 m tai tuntematon</td><td>{accuracy_dict['1']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['10']/total_count*100, 1)
    accuracy_table += f"<tr><td>10 m</td><td>{accuracy_dict['10']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['100']/total_count*100, 1)
    accuracy_table += f"<tr><td>100 m</td><td>{accuracy_dict['100']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['1000']/total_count*100, 1)
    accuracy_table += f"<tr><td>1 km</td><td>{accuracy_dict['1000']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['5000']/total_count*100, 1)
    accuracy_table += f"<tr><td>5 km</td><td>{accuracy_dict['5000']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['10000']/total_count*100, 1)
    accuracy_table += f"<tr><td>10 km</td><td>{accuracy_dict['10000']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['25000']/total_count*100, 1)
    accuracy_table += f"<tr><td>25 km</td><td>{accuracy_dict['25000']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['over']/total_count*100, 1)
    accuracy_table += f"<tr><td>yli 25 km</td><td>{accuracy_dict['over']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    accuracy_table += "</tbody></table>\n"

    return accuracy_table



def datechart_data(collection_id):

    # Note that this is the observation year, not the load date year. Aggregation is done by load date year.
    year = 2025

    # Get daily data from api. This lacks dates with zero count.
    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.firstLoadDate&orderBy=document.firstLoadDate&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=365&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&collectionId=http%3A%2F%2Ftun.fi%2F{ collection_id }&countryId=ML.206&yearMonth={ year }&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    data_dict = common_helpers.fetch_finbif_api(api_url, True)

    # Use day as key in dict
    data_by_days = dict()
    for item in data_dict["results"]:
        data_by_days[item["aggregateBy"]["document.firstLoadDate"]] = item["count"]

    cumulative_count = 0
    daily_count = 0
    cumulative_chartsj_data = []
    daily_chartsj_data = []

    # Loop all dates of the specified year, starting from 1.1. and ending to 31.12.
    for single_date in daterange(date(year, 1, 1)):
        if single_date.year != year:
            break

        if single_date.strftime("%Y-%m-%d") in data_by_days:
            count = data_by_days[single_date.strftime("%Y-%m-%d")]
        else:
            count = 0

        cumulative_count = cumulative_count + count
        daily_count = count # obs per day

        # JSON
        cumulative_chartsj_data.append(dict(x = single_date.strftime("%Y-%m-%d"), y = str(cumulative_count)))
        daily_chartsj_data.append(dict(x = single_date.strftime("%Y-%m-%d"), y = str(daily_count)))

    return json.dumps(cumulative_chartsj_data), json.dumps(daily_chartsj_data)


def main():
    html = dict()

    accuracy_data, total_count = common_atlas.coordinate_accuracy_data()
    html["accuracy_table"] = coordinate_accuracy_html(accuracy_data, total_count)

    html["collections_table"] = collections_data()

    html["cumulative_datechart_data_vihko"], html["daily_datechart_data_vihko"] = datechart_data("HR.4471,HR.1747")
#    html["cumulative_datechart_data_trip"], html["daily_datechart_data_trip"] = datechart_data("HR.1747")
    html["cumulative_datechart_data_tiira"], html["daily_datechart_data_tiira"] = datechart_data("HR.4412")
    html["cumulative_datechart_data_tipu"], html["daily_datechart_data_tipu"] = datechart_data("HR.48")

    return html
