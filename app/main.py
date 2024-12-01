from flask import Flask, render_template, redirect, request, make_response, session, g
#from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import sys
import traceback

import index.index

import login.login
import login.info

import atlas.atlas
import atlas.squareform
import atlas.misslist
import atlas.misslist_old
import atlas.here
import atlas.gps
import atlas.squaremap
import atlas.species
import atlas.specieslist
import atlas.singlespecies
import atlas.squares
import atlas.observers
import atlas.species_proportions
import atlas.completelists
import atlas.summap
import atlas.comparesquares

import taxa.taxa
import taxa.specieslist
import taxa.species
import taxa.new
import taxa.common_photos
import taxa.compare_years
import taxa.miss

import winterbird.winterbird
import winterbird.census

import info.info
import info.rain
import info.tower
import info.birds
import info.news

import weather.change

import my.year
import my.gps
import my.miss

import misc.bingo

#import viewer.viewer

#import pinna.pinna
#import pinna.contest_edit

#import dev.dev
#import dev.cache as devcache

import app_secrets

import requests

from redis.exceptions import ConnectionError
from functools import wraps

from helpers import common_helpers

def robust_cached(timeout=None, key_prefix='view/%s', unless=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Use the cached decorator as usual
                return cache.cached(timeout, key_prefix, unless)(f)(*args, **kwargs)
            except ConnectionError:
                # If a Redis connection error occurs, call the original function
                return f(*args, **kwargs)
        return decorated_function
    return decorator

# Redis cache
config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400, # Seconds
    "CACHE_REDIS_HOST": app_secrets.redis_host,
    "CACHE_REDIS_PORT": app_secrets.redis_port,
    "CACHE_REDIS_PASSWORD": app_secrets.redis_pass,
    "CACHE_REDIS_DB": 0,
    "CACHE_REDIS_URL": f"redis://{ app_secrets.redis_user }:{ app_secrets.redis_pass }@{ app_secrets.redis_host }:{ app_secrets.redis_port }",
}

app = Flask(__name__)
app.secret_key = app_secrets.flask_secret_key

app.config.from_mapping(config)
cache = Cache(app)

# Cache times:
 # 3600 = 1 h
 # 86400 = 24 h

print("-------------- PREPARE --------------", file = sys.stdout)

# This makes session token and user_data available on every template.
# TODO: Remove and user session variable instead?
@app.context_processor
def inject_token():
    token = session.get('token', None)
    user_data = session.get('user_data', None)
    return dict(session_token=token, user_data=user_data)

'''
@app.after_request
def set_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://unpkg.com 'unsafe-inline'; "
        "style-src 'self' https://unpkg.com 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' https://*.tile.osm.org/ data:; "
        "connect-src 'self' https://*.tile.osm.org; "
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    response.headers['Permissions-Policy'] = "geolocation=(), microphone=()"
    return response
'''

print("-------------- BEGIN --------------", file = sys.stdout)
# Pages

@app.route("/")
def root():
    html = index.index.main()
    return render_template("index.html", html=html)

@app.route("/login/<string:person_token_untrusted>")
def login_root(person_token_untrusted):
    session['token'] = person_token_untrusted
    # Get user data
    session['user_data'] = common_helpers.fetch_finbif_api(f"https://api.laji.fi/v0/person/{ person_token_untrusted }?access_token=")
    html = login.login.main(person_token_untrusted)
    return render_template("login.html", html=html)

@app.route("/login/info")
def login_info():
    user_data = session.get('user_data', None)
    html = login.info.main(user_data)
    return render_template("login_info.html", html=html)

@app.route("/logout")
def logout_root():
    session.clear()
    return redirect('/')

@app.route("/atlas")
@app.route("/atlas/")
@robust_cached(timeout=120)
def atlas_root():
    html = atlas.atlas.main()
    return render_template("atlas.html", html=html)

@app.route("/atlas/havaintosuhteet")
@app.route("/atlas/havaintosuhteet/")
@robust_cached(timeout=10800)
def species_proportions():
    html = atlas.species_proportions.main()
    return render_template("species_proportions.html", html=html)

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
# Redirect
def squareform_redirect(square_id_untrusted, show_untrusted):
    return redirect('/atlas/ruutulomake/' + square_id_untrusted + "/" + show_untrusted)

@app.route("/atlas/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
@robust_cached(timeout=3600)
def squareform(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    return render_template("squareform.html", html=html)


# TODO: Temporary test for making PDF's, remove of move to separate file
@app.route("/atlas/ruutupdf/<string:square_id_untrusted>/<string:show_untrusted>")
@robust_cached(timeout=1)
def squarepdf(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    html_page = render_template("squarepdf.html", html=html)
#    return html_page

    print(html_page)

    url = "https://api.laji.fi/v0/html-to-pdf?access_token=" + app_secrets.finbif_api_token
    data = html_page
    headers = {
        "Content-Type": "text/plain",
        "Accept": "application/pdf"
    }

    response = requests.post(url, data=data, headers=headers)
    print("Status Code:", response.status_code)
    print("Headers:", response.headers)
    print("Text:", response.text)

    res = make_response(response.content)
    res.headers.set('Content-Type', 'application/pdf')
    res.headers.set('Content-Disposition', 'inline; filename=ruutulomake.pdf')
    return res


@app.route("/atlas/gps")
@app.route("/atlas/gps/")
@robust_cached(timeout=1)
def gps():
    html = atlas.gps.main()
    return render_template("atlas_gps.html", html=html)

@app.route("/atlas/here/<string:square_id_untrusted>")
@robust_cached(timeout=3600)
def here(square_id_untrusted):
    html = atlas.here.main(square_id_untrusted)
    return render_template("atlas_here.html", html=html)

@app.route("/atlas/puutelista/<string:square_id_untrusted>")
@robust_cached(timeout=3600)
def misslist(square_id_untrusted):
    html = atlas.misslist.main(square_id_untrusted)
    return render_template("atlas_misslist.html", html=html)

@app.route("/atlas/puutelista_vanha/<string:square_id_untrusted>")
@robust_cached(timeout=3600)
def misslist_old(square_id_untrusted):
    html = atlas.misslist_old.main(square_id_untrusted)
    return render_template("atlas_misslist_old.html", html=html)

@app.route("/ruutu/<string:square_id_untrusted>")
# Redirect
def squaremap_redirect(square_id_untrusted):
    return redirect('/atlas/ruutu/' + square_id_untrusted)

@app.route("/atlas/ruutu/<string:square_id_untrusted>")
@robust_cached(timeout=10800)
def squaremap(square_id_untrusted):
    html = atlas.squaremap.main(square_id_untrusted)
    return render_template("squaremap.html", html=html)

@app.route("/atlas/lajiluettelo")
@app.route("/atlas/lajiluettelo/")
@robust_cached(timeout=10800)
def atlas_specieslist():
    html = atlas.specieslist.main()
    return render_template("atlas_specieslist.html", html=html)

@app.route("/atlas/laji/<string:species_name_untrusted>")
@robust_cached(timeout=86400) # 86400
def atlas_singlespecies(species_name_untrusted):
    html = atlas.singlespecies.main(species_name_untrusted)
    return render_template("atlas_singlespecies.html", html=html)

@app.route("/atlas/lajit")
@app.route("/atlas/lajit/")
@robust_cached(timeout=10800)
def atlas_species():
    html = atlas.species.main()
    return render_template("atlas_species.html", html=html)

@app.route("/atlas/ruudut")
@app.route("/atlas/ruudut/")
@robust_cached(timeout=10800)
def atlas_squares():
    html = atlas.squares.main()
    return render_template("atlas_squares.html", html=html)

@app.route("/atlas/havainnoijat")
@app.route("/atlas/havainnoijat/")
@robust_cached(timeout=10800)
def atlas_observers():
    html = atlas.observers.main()
    return render_template("atlas_observers.html", html=html)

@app.route("/atlas/listat")
@app.route("/atlas/listat/")
@robust_cached(timeout=10800)
def atlas_completelists():
    html = atlas.completelists.main()
    return render_template("atlas_completelists.html", html=html)

@app.route("/atlas/luokka/<string:class_untrusted>")
@robust_cached(timeout=10800)
def atlas_summap(class_untrusted):
    html = atlas.summap.main(class_untrusted)
    return render_template("atlas_summap.html", html=html)

@app.route("/atlas/ruutuvertailu/<string:society_untrusted>")
@robust_cached(timeout=43200) # 43200 = 12 h
def atlas_comparesquares(society_untrusted):
    html = atlas.comparesquares.main(society_untrusted)
    return render_template("atlas_comparesquares.html", html=html)

@app.route("/taxa/<string:taxon_id_untrusted>")
@robust_cached(timeout=86400) # 86400 = 24 h
def taxa_specieslist(taxon_id_untrusted):
    html = taxa.specieslist.main(taxon_id_untrusted)
    return render_template("taxa_specieslist.html", html=html)

@app.route("/taxa")
@app.route("/taxa/")
@robust_cached(timeout=10800) # 10800 = 3 h
def taxa_root():
    html = taxa.taxa.main()
    return render_template("taxa.html", html=html)

@app.route("/taxa/species/<string:taxon_id_untrusted>")
@robust_cached(timeout=86400) # 86400 = 24 h
def taxa_species(taxon_id_untrusted):
    html = taxa.species.main(taxon_id_untrusted)
    return render_template("taxa_species.html", html=html)

@app.route("/taxa/id/<string:page_name_untrusted>")
@robust_cached(timeout=86400)
def taxa_new(page_name_untrusted):
#    html = devcache.get_cached("/taxa/id/" + page_name_untrusted, 86400)
#    if not html:
#        html = taxa.new.main(page_name_untrusted)
#        devcache.set_cached("/taxa/id/" + page_name_untrusted, html)
    html = taxa.new.main(page_name_untrusted)
    return render_template("taxa_new.html", html=html)

@app.route("/taxa/photos_data/<string:taxon_id_untrusted>")
@robust_cached(timeout=10800)
def taxa_photos_data(taxon_id_untrusted):
    html = taxa.common_photos.main(taxon_id_untrusted)
    return render_template("taxa_photos_data.html", html=html)

@app.route("/taxa/compare_years/<string:taxon_id_untrusted>")
@robust_cached(timeout=10800)
def taxa_compare_years(taxon_id_untrusted):
    html = taxa.compare_years.main(taxon_id_untrusted)
    return render_template("taxa_compare_years.html", html=html)

@app.route("/taxa/miss")
@robust_cached(timeout=1)
def taxa_miss():
    lat_untrusted = request.args.get('lat')
    lon_untrusted = request.args.get('lon')
    taxon_untrusted = request.args.get('taxon')
    since_year_untrusted = request.args.get('since_year', 2000)
    near_km_untrusted = request.args.get('near', 50)
    far_km_untrusted = request.args.get('far', 100)
    html = taxa.miss.main(lat_untrusted, lon_untrusted, taxon_untrusted, since_year_untrusted, near_km_untrusted, far_km_untrusted)
    return render_template("taxa_miss.html", html=html)

@app.route("/weather/change/<int:messaging_on>")
@app.route("/weather/change")
def weather_change(messaging_on = 0):
    html = weather.change.main(messaging_on)
    return render_template("weather_change.html", html=html)

@app.route("/talvilinnut/<int:dev_secret>")
@app.route("/talvilinnut/")
@app.route("/talvilinnut")
@robust_cached(timeout=1) # 2592000 = 30 pv
def winterbird_root(dev_secret = 1):
    return redirect('/')
# Page removed due to too heavy API calls
#    html = winterbird.winterbird.main(dev_secret)
#    return render_template("winterbird.html", html=html)

@app.route("/talvilinnut/laskenta/<string:society_id>/<string:season>")
@app.route("/talvilinnut/laskenta/")
@app.route("/talvilinnut/laskenta")
@robust_cached(timeout=86400)
def winterbird_census(society_id = "", season = ""):
    html = winterbird.census.main(society_id, season)
    return render_template("winterbird_census.html", html=html)

@app.route("/info")
def info_root():
    html = info.info.main()
    return render_template("info.html", html=html)

@app.route("/info/rain")
@robust_cached(timeout=1) # 150 = 2½ min
def info_rain():
    html = info.rain.main()
    return render_template("info_rain.html", html=html)

@app.route("/info/tower")
@robust_cached(timeout=150) # 150 = 2½ min
def info_tower():
    html = info.tower.main()
    return render_template("info_tower.html", html=html)

@app.route("/info/birds/<string:secret>")
@robust_cached(timeout=3600) # 3600 = 1 h
def info_birds(secret = ""):
    html = info.birds.main(secret)
    return render_template("info_birds.html", html=html)

@app.route("/info/news")
@robust_cached(timeout=10800) # 10800 = 3h
def info_news():
    html = info.news.main()
    return render_template("info_news.html", html=html)

#@app.route("/dev/<string:taxon_id_untrusted>")
#@robust_cached(timeout=1)
#def dev_root(taxon_id_untrusted):
#    html = info.dev.main(taxon_id_untrusted)
#    return render_template("dev.html", html=html)

@app.route("/my/year/<int:year_untrusted>")
@app.route("/my/year/<int:year_untrusted>/")
@app.route("/my/year/<int:year_untrusted>/<string:taxon_id_untrusted>")
def my_year(year_untrusted, taxon_id_untrusted = "MX.37600"): # default = Biota
    token = session.get('token', None)
    html = my.year.main(token, year_untrusted, taxon_id_untrusted)
    return render_template("my_year.html", html=html)

@app.route("/my/gps")
@app.route("/my/gps/")
@robust_cached(timeout=1)
def my_gps():
    html = my.gps.main()
    return render_template("generic_gps.html", html=html)

@app.route("/my/<string:coord_untrusted>")
@robust_cached(timeout=1)
def my_here(coord_untrusted):
    html = my.here.main(coord_untrusted)
    return render_template("my_here.html", html=html)

@app.route("/bingo")
def bingo_root():
    html = misc.bingo.main()
    return render_template("misc_bingo.html", html=html)

'''
@app.route("/viewer/<path:document_id_untrusted>") # Note: path -> allows slashes in parameter
def viewer_root(document_id_untrusted):
    token = session.get('token', None)
    html = viewer.viewer.main(token, document_id_untrusted)
    return render_template("viewer.html", html=html)
'''

'''
@app.route("/pinna")
def pinna_root():
    token = session.get('token', None)
    html = pinna.pinna.main(token)
    return render_template("pinna.html", html=html)

@app.route("/pinna/contest/edit/<string:id_untrusted>")
def pinna_contest_edit(id_untrusted):
    token = session.get('token', None)
    html = pinna.contest_edit.main(token, id_untrusted)
    return render_template("pinna.html", html=html)
'''

'''
Debugging help:
- If getting error "AttributeError: 'function' object has no attribute", you have used same name for function and the file it calls. Use foo_root() or such name instead.
- 
'''

# Tools

@app.route("/robots.txt")
@robust_cached(timeout=86400)
def robots():
    return render_template("robots.txt")

@app.route("/flush")
def flush_cache():
    with app.app_context():
        cache.clear()
    return render_template("simple.html", content="Cache flushed")

# This should catch connection errors to FinBIF API, in case the error is not already handled elsewhere.
@app.errorhandler(ConnectionError)
def handle_bad_request(e):
    print("Havistin main error handler: ConnectionError " + str(e))
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Lajitietokeskuksen rajapinta ei juuri nyt toimi, yritä myöhemmin uudelleen (ConnectionError)', 503

# This should catch ValueEerors raised e.g. when user enters invalid data.
@app.errorhandler(ValueError)
def handle_value_error(e):
    print("Havistin main error handler: ValueError " + str(e), file = sys.stdout)
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Antamasi tieto on virheellinen (ruutu, lajin nimi, vuosiluku tms.) (ValueError)', 404

# This should cathc any generic errors raised in the app by 'raise Exception("Your custom error message")'
@app.errorhandler(Exception)
def handle_exception(e):
    # TODO: What tries to fetch this url? Something in Docker?
    if "wpad.dat" in request.url:
#        print(f"Havistin generic Exception for specific case url {request.url}: {str(e)}", file = sys.stdout)
        return "404", 404
    if "favicon.ico" in request.url:
#        print(f"Havistin generic Exception for specific case url {request.url}: {str(e)}", file = sys.stdout)
        return "404", 404
    print(f"Havistin generic Exception for url {request.url}: {str(e)}", file = sys.stdout)
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return "Lajitietokeskuksen rajapinta ei juuri nyt toimi, tai tässä palvelussa on jokin vika. Kokeile ladata sivu uudelleen tai yritä myöhemmin uudelleen. (Exception)", 500
