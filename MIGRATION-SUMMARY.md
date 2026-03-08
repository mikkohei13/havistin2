# FinBIF API v0 → v1 Migration Summary

## Core change: fetch_finbif_api() in common_helpers.py

access_token moved from URL query param to Authorization: Bearer header
lang query param extracted and sent as Accept-Language header
/v0/ base path stripped from URLs automatically
API-Version: 1 header added to all requests
New optional person_token param sends Person-Token header
Error detection changed from JSON body status field to r.status_code

## Authentication endpoints updated:

GET /v0/person/{personToken} → GET /person with Person-Token header (main.py)
GET /v0/person/by-id/{id} → GET /person/{id} (atlas/observers.py)

## Warehouse person token params migrated:

observerPersonToken={token} → selfAsObserver=true + Person-Token header (4 calls in my/year.py)
editorOrObserverPersonToken={token} → selfAsEditorOrObserver=true + Person-Token header (viewer/viewer.py)

## Error format updated in templates:

login.html: session['user_data']['error'] → session['user_data']['errorCode'] is defined
login_info.html: error in session['user_data'] → 'errorCode' in session['user_data']
viewer.py: data_dict.get("status", 0) → "errorCode" in data_dict

## URL cleanup across ~25 files:

Removed /v0/ prefix and access_token= suffix from all API URLs
Two special cases handled separately:
- routes/atlas.py squarepdf(): uses requests.post directly — added Authorization + API-Version headers, added missing import app_secrets
- templates/dev.html: JavaScript fetch() updated with headers and renamed /taxa/search params (onlySpecies→species, onlyFinnish→finnish, onlyInvasive→invasiveSpecies, removed observationMode)

## Bug fix:

index/index.py check_api(): also made direct requests.get() calls — updated to use Authorization header instead of appending token to URL (which broke after the URL cleanup removed &access_token=)