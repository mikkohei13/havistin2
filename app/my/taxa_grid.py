from helpers import common_helpers


MAX_SPECIES = 500


def fetch_finnish_species(taxon_id):
    url = f"https://api.laji.fi/taxa/{taxon_id}/species?checklist=MR.1&page=1&pageSize=1000&selectedFields=id%2CvernacularName%2CscientificName%2CobservationCountFinland%2CtaxonomicOrder&checklistVersion=current&finnish=true&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&includeHidden=false&sortOrder=taxonomic"
    return common_helpers.fetch_finbif_api(url)


def fetch_user_observed_ids(token, taxon_id):
    url = (
        f"https://api.laji.fi/warehouse/query/unit/aggregate"
        f"?countryId=ML.206&target={taxon_id}"
        f"&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL"
        f"&wild=WILD,WILD_UNKNOWN&individualCountMin=1"
        f"&aggregateBy=unit.linkings.taxon.speciesId"
        f"&cache=false&page=1&pageSize=2000"
        f"&qualityIssues=NO_ISSUES&onlyCount=true&selfAsObserver=true"
    )
    data = common_helpers.fetch_finbif_api(url, person_token=token)
    ids = set()
    for row in data.get("results", []):
        species_id = row.get("aggregateBy", {}).get("unit.linkings.taxon.speciesId")
        if species_id:
            ids.add(str(species_id).replace("http://tun.fi/", ""))
    return ids


def prepare_species(results, observed_ids):
    if len(results) > MAX_SPECIES:
        results = sorted(
            results,
            key=lambda s: s.get("observationCountFinland") or 0,
            reverse=True,
        )[:MAX_SPECIES]
        results = sorted(results, key=lambda s: s.get("taxonomicOrder") or 0)

    species = []
    for item in results:
        sid = item["id"]
        species.append({
            "id": sid,
            "scientific_name": item.get("scientificName", ""),
            "vernacular_name": item.get("vernacularName") or "ei suomenkielistä nimeä",
            "obs_count": item.get("observationCountFinland") or 0,
            "taxonomic_order": item.get("taxonomicOrder") or 0,
            "observed": sid in observed_ids,
        })
    return species


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

    species_data = fetch_finnish_species(taxon_id)
    observed_ids = fetch_user_observed_ids(token, taxon_id)
    species = prepare_species(species_data.get("results", []), observed_ids)

    html["taxon_id"] = taxon_id
    html["scientific_name"] = taxon.get("scientificName", "")
    html["vernacular_name"] = taxon.get("vernacularName", "")
    html["finnish_species_count"] = taxon.get("countOfFinnishSpecies", len(species))
    html["species"] = species
    html["shown_count"] = len(species)
    html["observed_count"] = sum(1 for s in species if s["observed"])
    return html
