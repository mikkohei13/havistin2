from flask import Flask, render_template, redirect, request
#from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import sys
import traceback

import index.index

import atlas.atlas
import atlas.squareform
import atlas.misslist
import atlas.squaremap
import atlas.species
import atlas.specieslist
import atlas.singlespecies
import atlas.squares
import atlas.observers
import atlas.species_proportions
import atlas.completelists
import atlas.summap

import taxa.taxa
import taxa.specieslist
import taxa.species
import taxa.new
import taxa.common_photos

import winterbird.winterbird
import winterbird.census

import weather.change

import dev.dev
import app_secrets
#import dev.cache as devcache

#import app_secrets

'''
# Filesystem cache (works inconsistently on services that have ephemeral storage)
config = {
    "DEBUG": True,
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "/havistin2/app/cache",
    "CACHE_DEFAULT_TIMEOUT": 600 # Seconds
}
'''

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

app.config.from_mapping(config)
cache = Cache(app)

# Cache times:
 # 3600 = 1 h
 # 86400 = 24 h

print("-------------- BEGIN --------------", file = sys.stdout)

# Pages

@app.route("/")
def root():
    html = index.index.main()
    return render_template("index.html", html=html)

@app.route("/atlas")
@app.route("/atlas/")
@cache.cached(timeout=1)
def atlas_root():
    html = atlas.atlas.main()
    return render_template("atlas.html", html=html)

@app.route("/atlas/havaintosuhteet")
@app.route("/atlas/havaintosuhteet/")
@cache.cached(timeout=3600)
def species_proportions():
    html = atlas.species_proportions.main()
    return render_template("species_proportions.html", html=html)

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
# Redirect
def squareform_redirect(square_id_untrusted, show_untrusted):
    return redirect('/atlas/ruutulomake/' + square_id_untrusted + "/" + show_untrusted)

@app.route("/atlas/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
@cache.cached(timeout=86400)
def squareform(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    return render_template("squareform.html", html=html)

@app.route("/atlas/puutelista/<string:square_id_untrusted>")
@cache.cached(timeout=86400)
def misslist(square_id_untrusted):
    html = atlas.misslist.main(square_id_untrusted)
    return render_template("atlas_misslist.html", html=html)

@app.route("/ruutu/<string:square_id_untrusted>")
# Redirect
def squaremap_redirect(square_id_untrusted):
    return redirect('/atlas/ruutu/' + square_id_untrusted)

@app.route("/atlas/ruutu/<string:square_id_untrusted>")
@cache.cached(timeout=3600)
def squaremap(square_id_untrusted):
    html = atlas.squaremap.main(square_id_untrusted)
    return render_template("squaremap.html", html=html)

@app.route("/atlas/lajiluettelo")
@app.route("/atlas/lajiluettelo/")
@cache.cached(timeout=3600)
def atlas_specieslist():
    html = atlas.specieslist.main()
    return render_template("atlas_specieslist.html", html=html)

@app.route("/atlas/laji/<string:species_name_untrusted>")
@cache.cached(timeout=86400) # 86400
def atlas_singlespecies(species_name_untrusted):
    html = atlas.singlespecies.main(species_name_untrusted)
    return render_template("atlas_singlespecies.html", html=html)

@app.route("/atlas/lajit")
@app.route("/atlas/lajit/")
@cache.cached(timeout=3600)
def atlas_species():
    html = atlas.species.main()
    return render_template("atlas_species.html", html=html)

@app.route("/atlas/ruudut")
@app.route("/atlas/ruudut/")
@cache.cached(timeout=3600)
def atlas_squares():
    html = atlas.squares.main()
    return render_template("atlas_squares.html", html=html)

@app.route("/atlas/havainnoijat")
@app.route("/atlas/havainnoijat/")
@cache.cached(timeout=3600)
def atlas_observers():
    html = atlas.observers.main()
    return render_template("atlas_observers.html", html=html)

@app.route("/atlas/listat")
@app.route("/atlas/listat/")
@cache.cached(timeout=3600)
def atlas_completelists():
    html = atlas.completelists.main()
    return render_template("atlas_completelists.html", html=html)

@app.route("/atlas/luokka/<string:class_untrusted>")
@cache.cached(timeout=3600)
def atlas_summap(class_untrusted):
    html = atlas.summap.main(class_untrusted)
    return render_template("atlas_summap.html", html=html)

@app.route("/taxa/<string:taxon_id_untrusted>")
@cache.cached(timeout=86400)
def taxa_specieslist(taxon_id_untrusted):
    html = taxa.specieslist.main(taxon_id_untrusted)
    return render_template("taxa_specieslist.html", html=html)

@app.route("/taxa")
@app.route("/taxa/")
@cache.cached(timeout=3600)
def taxa_root():
    html = taxa.taxa.main()
    return render_template("taxa.html", html=html)

@app.route("/taxa/species/<string:taxon_id_untrusted>")
@cache.cached(timeout=86400)
def taxa_species(taxon_id_untrusted):
    html = taxa.species.main(taxon_id_untrusted)
    return render_template("taxa_species.html", html=html)

@app.route("/taxa/id/<string:page_name_untrusted>")
@cache.cached(timeout=86400)
def taxa_new(page_name_untrusted):
#    html = devcache.get_cached("/taxa/id/" + page_name_untrusted, 86400)
#    if not html:
#        html = taxa.new.main(page_name_untrusted)
#        devcache.set_cached("/taxa/id/" + page_name_untrusted, html)
    html = taxa.new.main(page_name_untrusted)
    return render_template("taxa_new.html", html=html)

@app.route("/taxa/photos_data/<string:taxon_id_untrusted>")
@cache.cached(timeout=3600)
def taxa_photos_data(taxon_id_untrusted):
    html = taxa.common_photos.main(taxon_id_untrusted)
    return render_template("taxa_photos_data.html", html=html)

@app.route("/weather/change/<int:messaging_on>")
@app.route("/weather/change")
def weather_change(messaging_on = 0):
    html = weather.change.main(messaging_on)
    return render_template("weather_change.html", html=html)

@app.route("/talvilinnut/<int:dev_secret>")
@app.route("/talvilinnut/")
@app.route("/talvilinnut")
@cache.cached(timeout=86400)
def winterbird_root(dev_secret = 1):
    html = winterbird.winterbird.main(dev_secret)
    return render_template("winterbird.html", html=html)

@app.route("/talvilinnut/laskenta/<string:society_id>/<string:season>")
@app.route("/talvilinnut/laskenta/")
@app.route("/talvilinnut/laskenta")
@cache.cached(timeout=86400)
def winterbird_census(society_id = "", season = ""):
    html = winterbird.census.main(society_id, season)
    return render_template("winterbird_census.html", html=html)

@app.route("/dev/<string:taxon_id_untrusted>")
@cache.cached(timeout=1)
def dev_root(taxon_id_untrusted):
    html = dev.dev.main(taxon_id_untrusted)
    return render_template("dev.html", html=html)

'''
Debugging help:
- If getting error "AttributeError: 'function' object has no attribute", you have used same name for function and the file it calls. Use foo_root() or such name instead.
- 
'''

# Tools

@app.route("/robots.txt")
@cache.cached(timeout=86400)
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
    return "Lajitietokeskuksen rajapinta ei juuri nyt toimi, tai tässä palvelussa on jokin vika. Ole hyvä ja yritä myöhemmin uudelleen. (Exception)", 500
