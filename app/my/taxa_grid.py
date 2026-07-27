from helpers import common_helpers


GRID_MAX = 250
TOP_N = 10
SPECIES_PAGE_SIZE = 1000
USER_AGG_PAGE_SIZE = 2000


def fetch_finnish_species_page(taxon_id, page):
    url = (
        f"https://api.laji.fi/taxa/{taxon_id}/species"
        f"?checklist=MR.1&page={page}&pageSize={SPECIES_PAGE_SIZE}"
        f"&selectedFields=id,vernacularName,scientificName,observationCountFinland,taxonomicOrder,taxonRank"
        f"&checklistVersion=current&finnish=true&includeMedia=false&includeDescriptions=false"
        f"&includeRedListEvaluations=false&includeHidden=false&sortOrder=taxonomic"
    )
    data = common_helpers.fetch_finbif_api(url)
    data["results"] = [
        item for item in data.get("results", [])
        if item.get("taxonRank") == "MX.species"
    ]
    return data


def fetch_all_finnish_species(taxon_id):
    page = 1
    all_results = []
    while True:
        data = fetch_finnish_species_page(taxon_id, page)
        all_results.extend(data.get("results", []))
        if data.get("currentPage", page) >= data.get("lastPage", page):
            break
        page += 1
    return all_results


def fetch_user_observed_counts(token, taxon_id):
    counts = {}
    page = 1
    while True:
        url = (
            f"https://api.laji.fi/warehouse/query/unit/aggregate"
            f"?countryId=ML.206&target={taxon_id}"
            f"&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL"
            f"&wild=WILD,WILD_UNKNOWN&individualCountMin=1"
            f"&aggregateBy=unit.linkings.taxon.speciesId"
            f"&cache=false&page={page}&pageSize={USER_AGG_PAGE_SIZE}"
            f"&qualityIssues=NO_ISSUES&onlyCount=true&selfAsObserver=true"
        )
        data = common_helpers.fetch_finbif_api(url, person_token=token)
        rows = data.get("results", [])
        if not rows:
            break
        for row in rows:
            species_id = row.get("aggregateBy", {}).get("unit.linkings.taxon.speciesId")
            if species_id:
                sid = str(species_id).replace("http://tun.fi/", "")
                counts[sid] = row.get("count", 0)
        if data.get("currentPage", page) >= data.get("lastPage", page):
            break
        page += 1
    return counts


def build_species_list(results, user_counts):
    species = []
    for item in results:
        sid = item["id"]
        user_obs_count = user_counts.get(sid, 0)
        species.append({
            "id": sid,
            "scientific_name": item.get("scientificName", ""),
            "vernacular_name": item.get("vernacularName") or "ei suomenkielistä nimeä",
            "obs_count": item.get("observationCountFinland") or 0,
            "taxonomic_order": item.get("taxonomicOrder") or 0,
            "observed": user_obs_count > 0,
            "user_obs_count": user_obs_count,
        })
    return species


def prepare_display(species):
    if len(species) <= GRID_MAX:
        return {
            "mode": "grid",
            "species": species,
        }

    observed = [s for s in species if s["observed"]]
    missing = [s for s in species if not s["observed"]]

    sections = [
        {
            "title": "Eniten havaitsemasi lajit",
            "species": sorted(observed, key=lambda s: s["user_obs_count"], reverse=True)[:TOP_N],
        },
        {
            "title": "Harvinaisimmat havaitsemasi lajit",
            "species": sorted(observed, key=lambda s: s["obs_count"])[:TOP_N],
        },
        {
            "title": "Yleisimmät havaitsemattomat lajit",
            "species": sorted(missing, key=lambda s: s["obs_count"], reverse=True)[:TOP_N],
        },
    ]

    return {
        "mode": "summary",
        "sections": [s for s in sections if s["species"]],
    }


def main(token, taxon_id_untrusted):
    html = {"needs_login": False}

    if not token:
        html["needs_login"] = True
        return html

    taxon_id = common_helpers.valid_qname(taxon_id_untrusted)

    taxon = common_helpers.fetch_finbif_api(
        f"https://api.laji.fi/taxa/{taxon_id}"
        f"?lang=fi&langFallback=true&maxLevel=0&includeHidden=false"
        f"&includeMedia=false&includeDescriptions=false"
        f"&includeRedListEvaluations=false&sortOrder=taxonomic"
    )

    species_results = fetch_all_finnish_species(taxon_id)
    user_counts = fetch_user_observed_counts(token, taxon_id)
    species = build_species_list(species_results, user_counts)
    display = prepare_display(species)

    html["taxon_id"] = taxon_id
    html["scientific_name"] = taxon.get("scientificName", "")
    html["vernacular_name"] = taxon.get("vernacularName", "")
    html["finnish_species_count"] = taxon.get("countOfFinnishSpecies", len(species))
    html["observed_count"] = sum(1 for s in species if s["observed"])
    html["mode"] = display["mode"]
    html["species"] = display.get("species", [])
    html["sections"] = display.get("sections", [])
    return html
