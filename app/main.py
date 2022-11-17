from flask import Flask, render_template, redirect
#from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import sys
import traceback

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

import taxa.taxa
import taxa.specieslist
import taxa.species
import taxa.new
import taxa.common_photos

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

print("-------------- BEGIN -------------- --------------", file = sys.stdout)

# Pages

@app.route("/")
@cache.cached(timeout=3600) # 3600
def root():
    html = atlas.atlas.main()
    return render_template("index.html", html=html)

@app.route("/atlas/havaintosuhteet")
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
@cache.cached(timeout=3600)
def atlas_specieslist():
    html = atlas.specieslist.main()
    return render_template("atlas_specieslist.html", html=html)

@app.route("/atlas/laji/<string:species_name_untrusted>")
@cache.cached(timeout=3600)
def atlas_singlespecies(species_name_untrusted):
    html = atlas.singlespecies.main(species_name_untrusted)
    return render_template("atlas_singlespecies.html", html=html)

@app.route("/atlas/lajit")
@cache.cached(timeout=3600)
def atlas_species():
    html = atlas.species.main()
    return render_template("atlas_species.html", html=html)

@app.route("/atlas/ruudut")
@cache.cached(timeout=3600)
def atlas_squares():
    html = atlas.squares.main()
    return render_template("atlas_squares.html", html=html)

@app.route("/atlas/havainnoijat")
@cache.cached(timeout=3600)
def atlas_observers():
    html = atlas.observers.main()
    return render_template("atlas_observers.html", html=html)

@app.route("/taxa/<string:taxon_id_untrusted>")
@cache.cached(timeout=3600)
def taxa_specieslist(taxon_id_untrusted):
    html = taxa.specieslist.main(taxon_id_untrusted)
    return render_template("taxa_specieslist.html", html=html)

@app.route("/taxa")
@cache.cached(timeout=10)
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

@app.route("/dev/<string:taxon_id_untrusted>")
@cache.cached(timeout=60)
def dev_root(taxon_id_untrusted):
#    html = devcache.get_cached("/dev/" + taxon_id_untrusted)
#    if not html:
#        html = dev.dev.main(taxon_id_untrusted)
#        devcache.set_cached("/dev/" + taxon_id_untrusted, html)
    html = dev.dev.main(taxon_id_untrusted)
    return render_template("dev.html", html=html)

# If getting error "AttributeError: 'function' object has no attribute", you have used same name for function and the file it calls. Use foo_root() or such name instead.

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

@app.errorhandler(ValueError)
def handle_exception(e):
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Tarkista antamasi ruudun numero tai lajin nimi. Haettua sivua ei löydy (404)', 404

# Todo: why does not catch the error?
@app.errorhandler(ConnectionError)
def handle_bad_request(e):
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Lajitietokeskuksen rajapinta ei juuri nyt toimi, yritä myöhemmin uudelleen (503)', 503
