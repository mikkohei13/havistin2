# Technical overview of `/my/groups/{year}/{rank}`

Personal taxon-group summary: how many observations the logged-in user (and everyone in Finland) has at phylum / class / order / family level.

## Routing (Flask)

- `main.py`: `GET /my/groups/<year>/<rank>` (optional trailing slash).
- Requires Laji.fi **Person-Token** in session (`session['token']`); without it, template shows `needs_login`.

## Server logic (`app/my/groups.py`)

`main(token, year_untrusted, rank_untrusted)`:

- Clamps **year** to 1900…current calendar year.
- Normalizes **rank** to `phylum` | `class` | `order` | `family` (invalid → `family`).

Shared FinBIF filters on warehouse aggregates: `countryId=ML.206`, `target=MX.37600` (Biota) or comma-separated MX ids, `individualCountMin=1`, identification/subtaxa flags, `qualityIssues=NO_ISSUES`, paginated (`pageSize=1000`) until a short page or `currentPage >= lastPage`.

**Aggregate field** by rank (`unit.linkings.taxon.*`): `phylumId`, `classId`, `orderId`, `familyId`.

### Which taxa appear in the table

One row per taxon at this rank with **public** observations in Finland since `PUBLIC_COUNT_TIME_FROM` (`fetch_full_public_counts` with `public_count_time_filter()`, `selfAsObserver=false`, full Biota paginated aggregate). Row set does **not** change when the user picks another year.

User counts for those ids: full Biota paginated aggregates with `selfAsObserver=true` — selected **year** for `count`, no time filter for `count_all` (may be 0 on a row).

### Observer vs public API calls

| Helper | `selfAsObserver` | `Person-Token` | Typical `time` | `target` |
|--------|------------------|----------------|----------------|----------|
| `fetch_aggregate_pages(..., self_as_observer=True)` | yes | yes | year / none / per-chunk | Biota or id list |
| `fetch_aggregate_pages(..., self_as_observer=False)` | no | no | see below | Biota or id list |
| `fetch_full_public_counts` | no | no | `public_count_time_filter()` (row set + `count_public`) | Biota |
| `fetch_aggregate_pages(..., self_as_observer=True)` | yes | yes | year / none | Biota (`count`, `count_all`) |
| `fetch_observer_counts_for_taxa` | yes | yes | year / none | id list (chunks) — unused in `main` |
| `fetch_public_counts_for_taxa` | no | no | `public_count_time_filter()` | id list (chunks) — unused in `main` |

**Public column time filter** (fixed, independent of selected year): `PUBLIC_COUNT_TIME_FROM=2000` through current year — warehouse `time=2000/{end_year}`, Laji links `public_time_laji` = `2000-01-01/{end_year}-12-31`.

### Per-row fields (`html["rank_taxa"]`)

| Field | Meaning |
|-------|---------|
| `id` | MX qname (from aggregate URI, `http://tun.fi/` stripped) |
| `count` | User’s observations, **selected year** |
| `count_all` | User’s observations, **all years** |
| `count_public` | **All observers**, Finland, **2000–current year** |
| `fi`, `sci` | From batched `GET /taxa?id=…` (no person token) |
| `taxonomic_order` | `taxonomicOrder` from `/taxa` |

**`html["mx_qnames_not_in_year"]`**: MX ids with `count == 0` and `count_all > 0` (user has lifetime observations but none in selected year). Used for Laji list links (`observerPersonToken=true` on the “omat” link).

Default **server sort**: `-count_public`, `-count`, taxonomic order, name.

Taxa lookup failures still render rows with empty names.

**Summary counts** (`taxacount_own_year`, `taxacount_own_all`, `taxacount_public`): count rows in `merged` where the corresponding column is &gt; 0 (same rows as the table).

## Template / client (`my_groups.html`)

Navigation form: year, rank. **Siirry** → `/my/groups/{year}/{rank}`. JS reads path to pre-fill controls.

Table `#my-groups-taxa-table`; client-side sort on header click (`data-sort-*` on rows). Default sort: `countPublic` desc.

**Laji links** (`observation/species`):

- User year column: `time={year}-01-01/{year}-12-31`, `observerPersonToken=true`.
- User all-years column: no `time`, `observerPersonToken=true`.
- Suomessa (2000–): `time={public_time_laji}`, no observer token.

States: `needs_login`, `api_error`, `got_results` (table), or empty message.
