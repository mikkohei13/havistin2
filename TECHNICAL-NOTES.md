# Technical overview of /my/groups/{year}/{rank}

## Routing (Flask)

main.py exposes /my/groups/<year>/<rank> (and trailing slash).

# Server logic (app/my/groups.py)

main(token, year_untrusted, rank_untrusted) clamps the year, normalizes rank to one of phylum | class | order | family (invalid → family), and sets copy/title fields for the template.
If there is no session token, it skips FinBIF and sets needs_login.
Otherwise it calls fetch_finbif_api(..., person_token=token) on GET https://api.laji.fi/warehouse/query/unit/aggregate twice: (1) with time={year}, (2) with no time filter (all years), both with selfAsObserver=true, countryId=ML.206, target=MX.37600 (Biota) + usual annotation/subtaxa flags, aggregateBy / selected set from rank (phylumId, classId, orderId, or familyId on unit.linkings.taxon).
It pages until a short page or currentPage >= lastPage (page size 1000).
Each row’s aggregate key is turned into an MX qname; the table is the union of taxa from both responses, with per-year and all-years counts; sorted by descending year count, then all-years count, then name.
Names come from batched GET https://api.laji.fi/taxa?id=… (chunks, no person token), mapping vernacularName / scientificName. Failures there still show rows with empty names.

## Template/Client (my_groups.html)

Small JS reads the path /my/groups/{year}/{rank}, pre-fills year + rank, and Siirry navigates to the same pattern.
Jinja renders login / API error / empty / table states; the table is the sorted list plus links to Laji (map uses observerPersonToken=true in the URL; the selected-year column adds a calendar-year time filter, the all-years column does not).