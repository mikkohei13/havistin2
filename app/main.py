from flask import Flask, render_template, redirect, request, session, g
#from werkzeug.exceptions import HTTPException
from extensions import cache
from decorators import robust_cached

import sys
import traceback

import index.index

import login.login
import login.info

import taxa.taxa
import taxa.specieslist
import taxa.species
import taxa.new
import taxa.common_photos
import taxa.compare_years
import taxa.miss

import winterbird.winterbird
import winterbird.census

import weather.change

import my.year
import my.gps
import my.miss

import misc.bingo

import app_secrets

from redis.exceptions import ConnectionError
from functools import wraps

from helpers import common_helpers
from decorators import robust_cached

# Routes
from app.routes.info import info_bp
from app.routes.atlas import atlas_bp
from app.routes.taxa import taxa_bp


print("-------------- PREPARE --------------", file = sys.stdout)

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
app.config.from_mapping(config)  # Apply Redis config first
cache.init_app(app)  # Initialize cache with the Redis config

app.secret_key = app_secrets.flask_secret_key

# This makes session token and user_data available on every template.
# TODO: Remove and user session variable instead?
@app.context_processor
def inject_token():
    token = session.get('token', None)
    user_data = session.get('user_data', None)
    return dict(session_token=token, user_data=user_data)


'''
Debugging help:
- If getting error "AttributeError: 'function' object has no attribute", you have used same name for function and the file it calls. Use foo_root() or such name instead.
- 
'''

print("-------------- PAGES --------------", file = sys.stdout)

@app.route("/")
def root():
    html = index.index.main()
    return render_template("index.html", html=html)

# Blueprints
app.register_blueprint(info_bp)
app.register_blueprint(atlas_bp)
app.register_blueprint(taxa_bp)

# Old squareform route, redirect to new route
@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
def squareform_redirect(square_id_untrusted, show_untrusted):
    return redirect('/atlas/ruutulomake/' + square_id_untrusted + "/" + show_untrusted)

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
