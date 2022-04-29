
import requests
from datetime import timedelta, date
import time
import json
import sys
import asyncio


import app_secrets

def fetch_api(api_url):
    api_url = api_url + app_secrets.finbif_api_token
    print(api_url, file = sys.stdout) # debug

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: api.laji.fi complete error.", file = sys.stdout)

#    r.encoding = encoding
    dataJson = r.text
    dataDict = json.loads(dataJson)

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("ERROR: api.laji.fi 403 error.", file = sys.stdout)
            raise ConnectionError

#    print(dataDict, file = sys.stdout)
    return dataDict


def convert_collection_name(id):
    if "http://tun.fi/HR.4412" == id:
        return "Tiira"
    elif  "http://tun.fi/HR.4471" == id:
        return "Vihko, lintuatlaslomake"
    elif  "http://tun.fi/HR.1747" == id:
        return "Vihko, retkilomake"
    elif  "http://tun.fi/HR.3211" == id:
        return "iNaturalist Suomi"
    else:
        return "Muu"


async def collections_data():
    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.collectionId&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    dataDict = fetch_api(api_url)

    total_obs_count = 0
    for i in dataDict["results"]:
        total_obs_count = total_obs_count + i["count"]

    collections_table = "<h3>Havaintolähteet</h3>"
    collections_table += "<table class='styled-table'>"
    collections_table += "<thead><tr><th>Järjestelmä</th><th>Havaintoja</th><th>%</th></tr></thead>"
    collections_table += "<tbody>"

    for i in dataDict["results"]:
        collections_table += "<tr><td>" + convert_collection_name(i["aggregateBy"]["document.collectionId"]) + "</td>"
        collections_table += "<td>" + str(i["count"]) + "</td>"
        collections_table += "<td>" + str(round((i["count"] / total_obs_count) * 100, 1)) + " %</td></tr>"
#        print(dataDict["results"]["aggregateBy"]["count"], file = sys.stdout)

    collections_table += "</tbody></table>"

    return collections_table

'''
def breeding_data(atlas_class):

    if "D" == atlas_class:
        atlas_class = "MY.atlasClassEnumD"
    elif "C" == atlas_class:
        atlas_class = "MY.atlasClassEnumC"
    # TODO: exception for other cases

    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=20&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=" + atlas_class + "&access_token="

    dataDict = fetch_api(api_url)

    breeding_dict = dict()
    for item in dataDict["results"]:
        breeding_dict[item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]] = item["count"]

    return breeding_dict
'''

async def breeding_html(atlas_class):

    if "MY.atlasClassEnumD" == atlas_class:
        heading = "Varmat pesinnät"
    elif "MY.atlasClassEnumC" == atlas_class:
        heading = "Todennäköiset pesinnät"
    # TODO: exception for other cases

    data = fetch_api("https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=20&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=" + atlas_class + "&access_token=")

    html = f"<h3>{heading} (top 20)</h3>"
    html += "<p>Näistä lajeista on tehty eniten havaintoja viimeisen kahden viikon aikana, eli niitä kannattaa erityisesti tarkkailla. Arkaluontoiset havainnot eivät ole tässä taulukossa mukana.</p>"
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


async def recent_observers():
    # observations loaded to FinBIF during last 48 hours, excluding Tiira
    # 48 h: 172800
    timestamp = int(time.time()) -172800

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.team.memberName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=20&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&firstLoadedSameOrAfter={timestamp}&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumA%2CMY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&collectionIdNot=HR.4412&access_token="

    data = fetch_api(url)

    html = f"<h3>Aktiiviset havainnoijat 2 vrk aikana (top 20)</h3>"
    html += "<p>Eniten havaintoja viimeisen 48 tunnin aikana tehneet henkilöt niistä havainnoista, joissa on julkinen nimitieto Lajitietokeskuksen tietovarastossa. Laskennassa ei ole mukana arkaluontoisia havaintoja, ja käyttäjä on voinut myös itse salata nimensä Vihkossa havaintoeräkohtaisesti. Lisää havainnoijatilastoja <a href='https://digitalis.fi/lintuatlas/havainnoijat/'>Digitaliksen sivuilla</a>.</p>"
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Havainnoija</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["gathering.team.memberName"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


async def societies():
    # TODO: All observations per society, requires new api endpoint from laji.fi
    # Tiira observations
    url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.team.memberName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=50&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumA%2CMY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&collectionId=HR.4412&access_token="

    data = fetch_api(url)

    html = f"<h3>Tiiran havainnot yhdistyksittäin</h3>"
    html += "<p>Tiirasta tulevissa atlashavainnoissa havainnoijan nimenä on paikallinen lintuyhdistys.</p>"
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Yhdistys</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["gathering.team.memberName"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def square_data():

    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.ykj10km.lat%2Cgathering.conversions.ykj10km.lon&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=10&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    dataDict = fetch_api(api_url)

    square_dict = dict()
    for item in dataDict["results"]:
        lat = item["aggregateBy"]["gathering.conversions.ykj10km.lat"][0:3]
        lon = item["aggregateBy"]["gathering.conversions.ykj10km.lon"][0:3]
        square_id = str(lat) + ":" + str(lon)
        square_dict[square_id] = item["count"]

    return square_dict


def square_html(dataDict):

    html = f"<h3>Atlasruudut, joista eniten havaintoja (top 10)</h3>"
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Ruutu</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for key, value in dataDict.items():
        html += "<tr><td>" + key + "</td>"
        html += "<td>" + str(value) + "</td>"

    html += "</tbody></table>"
    return html


def daterange(start_date):
    end_date = date.today()

    # inclusive end
    day_count = int((end_date - start_date).days) + 1

    for n in range(day_count):
        yield start_date + timedelta(n)


def coordinate_accuracy_data():
    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.interpretations.coordinateAccuracy&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    dataDict = fetch_api(api_url)

    accuracy_dict = dict()
    total_count = 0
    for item in dataDict["results"]:
        accuracy_text = ""        
        accuracy = int(item["aggregateBy"]["gathering.interpretations.coordinateAccuracy"])
        count = item["count"]
        total_count = total_count + count

        if accuracy == 1:
            accuracy_text = "unk"
        elif accuracy <= 10:
            accuracy_text = "10"
        elif accuracy <= 100:
            accuracy_text = "100"
        elif accuracy <= 1000:
            accuracy_text = "1000"
        elif accuracy <= 5000:
            accuracy_text = "5000"
        elif accuracy <= 10000:
            accuracy_text = "10000"
        elif accuracy <= 25000:
            accuracy_text = "25000"
        else:
            accuracy_text = "over"

        # Todo: better way to do this?    
        if accuracy_text in accuracy_dict:
            accuracy_dict[accuracy_text] = accuracy_dict[accuracy_text] + count
        else:
            accuracy_dict[accuracy_text] = count

    return accuracy_dict, total_count


def coordinate_accuracy_html(accuracy_dict, total_count):

    accuracy_table = "\n\n<h3>Havaintojen julkinen tarkkuus</h3>\n"
    accuracy_table += "<p>Mitä tarkempi havainnon paikka on, sitä paremmin sitä voidaan hyödyntää esim suojelutyössä. Tiirasta atlakseen tulee vain 10 km tasolle karkeistettuja havaintoja. Muista lähteistä arkaluontoiset sekä käyttäjien karkeistamat havainnot näkyvät tässä karkeistettuina, mutta suojelu- ym. käytössä ne ovat käytettävissä tarkkana.</p>\n"
    accuracy_table += "<table class='styled-table'>\n"
    accuracy_table += "<thead>\n<tr><th>Tarkkuus</th><th>Havaintoja</th><th>%</th><th> </th></tr>\n</thead>\n"
    accuracy_table += "<tbody>\n"

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
    accuracy_table += f"<tr><td>yli 25 m</td><td>{accuracy_dict['over']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    percentage = round(accuracy_dict['unk']/total_count*100, 1)
    accuracy_table += f"<tr><td>tuntematon</td><td>{accuracy_dict['unk']}</td><td>{percentage} %</td>\n"
    accuracy_table += "<td><span class='horizontal_bar' style='width: " + str(round(percentage)) + "px'>&nbsp;</span></td></tr>\n"

    accuracy_table += "</tbody></table>\n"

    return accuracy_table



async def datechart_data(collection_id):

    # Get daily data from api. This lacks dates with zero count.
    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.firstLoadDate&orderBy=document.firstLoadDate&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=365&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&collectionId=http%3A%2F%2Ftun.fi%2F{collection_id}&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    dataDict = fetch_api(api_url)

    # Use day as key in dict
    data_by_days = dict()
    for item in dataDict["results"]:
        data_by_days[item["aggregateBy"]["document.firstLoadDate"]] = item["count"]

    # Loop all dates so far, to generate chart.js data list.
    # If this date is changed, all observations before that are discarded.
    start_date = date(2022, 1, 1)

    cumulative_count = 0
    chartsj_data = []

    for single_date in daterange(start_date):

        if single_date.strftime("%Y-%m-%d") in data_by_days:
            count = data_by_days[single_date.strftime("%Y-%m-%d")]
        else:
            count = 0

        cumulative_count = cumulative_count + count

        # JSON
        daily = dict(x = single_date.strftime("%Y-%m-%d"), y = str(cumulative_count))
        chartsj_data.append(daily)

    json_data = json.dumps(chartsj_data)

    return json_data




async def main():
    html = dict()

#    breeding_data_dict = breeding_data("D")
#    html["breeding_certain"] = breeding_html("MY.atlasClassEnumD")

#    breeding_data_dict = breeding_data("C")

    task_collections_data = asyncio.create_task(collections_data())
    html["collections_table"] = await task_collections_data

    task_breeding_certain = asyncio.create_task(breeding_html("MY.atlasClassEnumD"))
    html["breeding_certain"] = await task_breeding_certain

    task_breeding_probable = asyncio.create_task(breeding_html("MY.atlasClassEnumC"))
    html["breeding_probable"] = await task_breeding_probable

    task_recent_observers = asyncio.create_task(recent_observers())
    html["recent_observers"] = await task_recent_observers

    task_societies = asyncio.create_task(societies())
    html["societies"] = await task_societies


#    html["recent_observers"] = recent_observers()
#    html["societies"] = societies()

    task_datechart_1 = asyncio.create_task(datechart_data("HR.4471"))
    html["datechart_data_birdatlas"] = await task_datechart_1

    task_datechart_2 = asyncio.create_task(datechart_data("HR.1747"))
    html["datechart_data_trip"] = await task_datechart_2

    task_datechart_3 = asyncio.create_task(datechart_data("HR.4412"))
    html["datechart_data_tiira"] = await task_datechart_3

    task_datechart_4 = asyncio.create_task(datechart_data("HR.3211"))
    html["datechart_data_inat"] = await task_datechart_4


    accuracy_data, total_count = coordinate_accuracy_data()
    html["accuracy_table"] = coordinate_accuracy_html(accuracy_data, total_count)

    square_data_dict = square_data()
    html["squares"] = square_html(square_data_dict)

    return html
