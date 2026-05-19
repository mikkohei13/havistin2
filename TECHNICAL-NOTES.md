# Technical overview of `/my/groups/{year}/{rank}`

Personal taxon-group summary: how many observations the logged-in user (and everyone in Finland) has at phylum / class / order / family level.

## Routing (Flask)

- `main.py`: `GET /my/groups/<year>/<rank>` (optional trailing slash).
- Query param **`scope`**: `mine` (default) or `all`. Passed to `my.groups.main(..., scope_untrusted=scope)`.
- Requires Laji.fi **Person-Token** in session (`session['token']`); without it, template shows `needs_login`.

## Server logic (`app/my/groups.py`)

`main(token, year_untrusted, rank_untrusted, scope_untrusted)`:

- Clamps **year** to 1900…current calendar year.
- Normalizes **rank** to `phylum` | `class` | `order` | `family` (invalid → `family`).
- Normalizes **scope** to `mine` | `all` (invalid → `mine`).

Shared FinBIF filters on warehouse aggregates: `countryId=ML.206`, `target=MX.37600` (Biota) or comma-separated MX ids, `individualCountMin=1`, identification/subtaxa flags, `qualityIssues=NO_ISSUES`, paginated (`pageSize=1000`) until a short page or `currentPage >= lastPage`.

**Aggregate field** by rank (`unit.linkings.taxon.*`): `phylumId`, `classId`, `orderId`, `familyId`.

### Which taxa appear in the table

| `scope` | Row set (`id_set`) |
|---------|-------------------|
| **`mine`** | Union of observer aggregates: taxa with **any** of the user’s observations in Finland at this rank — selected **year** OR **all years** (`selfAsObserver=true`, `Person-Token`, `target=Biota`). |
| **`all`** | All taxa at this rank with **public** observations in Finland in the **selected year** only (`selfAsObserver=false`, full Biota paginated aggregate, `time={year}`). User counts are then filled in per id (may be 0). |

After `id_set` is fixed, **public counts for every row** are loaded in one pass: `fetch_public_counts_for_taxa` with chunked `target=MX.1,MX.2,…` (50 ids per request).

### Observer vs public API calls

| Helper | `selfAsObserver` | `Person-Token` | Typical `time` | `target` |
|--------|------------------|----------------|----------------|----------|
| `fetch_aggregate_pages(..., self_as_observer=True)` | yes | yes | year / none / per-chunk | Biota or id list |
| `fetch_aggregate_pages(..., self_as_observer=False)` | no | no | see below | Biota or id list |
| `fetch_full_public_counts` | no | no | selected year | Biota |
| `fetch_observer_counts_for_taxa` | yes | yes | year / none | id list (chunks) |
| `fetch_public_counts_for_taxa` | no | no | `public_count_time_filter()` | id list (chunks) |

**Public column time filter** (fixed, independent of selected year): `PUBLIC_COUNT_TIME_FROM=2000` through current year — warehouse `time=2000/{end_year}`, Laji links `public_time_laji` = `2000-01-01/{end_year}-12-31`.

### Per-row fields (`html["families"]`)

| Field | Meaning |
|-------|---------|
| `id` | MX qname (from aggregate URI, `http://tun.fi/` stripped) |
| `count` | User’s observations, **selected year** |
| `count_all` | User’s observations, **all years** |
| `count_public` | **All observers**, Finland, **2000–current year** |
| `fi`, `sci` | From batched `GET /taxa?id=…` (no person token) |
| `taxonomic_order` | `taxonomicOrder` from `/taxa` |

**`html["families_count"]`**: rows with `count > 0` (user observed that group in the selected year).

**`html["mx_qnames_not_in_year"]`**: MX ids with `count == 0` and `count_all > 0` (user has lifetime observations but none in selected year). Used only in **`scope=mine`** for a Laji list link (`observerPersonToken=true`).

Default **server sort**:

- `mine`: `-count`, `-count_all`, taxonomic order, name.
- `all`: `-count_public`, `-count`, taxonomic order, name.

Taxa lookup failures still render rows with empty names.

## Template / client (`my_groups.html`)

Navigation form: year, rank, **Lista** (`scopeSelect`: “Vain omat havainnot” / “Kaikki Suomessa ({year})”). **Siirry** → `/my/groups/{year}/{rank}` or same with `?scope=all`. JS reads path + `scope` query to pre-fill controls.

Table `#my-groups-taxa-table` with `data-scope`; client-side sort on header click (`data-sort-*` on rows). Default sort: `countYear` desc (`mine`) or `countPublic` desc (`all`).

**Laji links** (`observation/species`):

- User year column: `time={year}-01-01/{year}-12-31`, `observerPersonToken=true`.
- User all-years column: no `time`, `observerPersonToken=true`.
- Suomessa (2000–): `time={public_time_laji}`, no observer token.

States: `needs_login`, `api_error`, `got_results` (table), or empty message.
