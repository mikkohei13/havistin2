from flask import Flask, render_template
#from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import sys
import traceback

import atlas.atlas
import atlas.squareform
import atlas.squaremap

#import app_secrets

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 600 # Seconds
}

app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)

@app.route("/")
@cache.cached(timeout=3600) # 1 h
def root():
    html = atlas.atlas.main()
    return render_template("index.html", html=html)

@app.route("/flush")
def flush_cache():
    with app.app_context():
        cache.clear()
    return render_template("simple.html", content="Cache flushed")

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
@cache.cached(timeout=86400) # 24 h
def squareform(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    return render_template("squareform.html", html=html)

@app.route("/ruutu/<string:square_id_untrusted>")
@cache.cached(timeout=3600) # 1 h
def squaremap(square_id_untrusted):
    html = atlas.squaremap.main(square_id_untrusted)
    return render_template("squaremap.html", html=html)

@app.errorhandler(ValueError)
def handle_exception(e):
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Tarkista antamasi ruudun numero tai lajin nimi. Haettua sivua ei löydy (404)', 404

# Todo: why does not catch the error?
@app.errorhandler(ConnectionError)
def handle_bad_request(e):
    print(traceback.format_exc(), sep="\n", file = sys.stdout)
    return 'Lajitietokeskuksen rajapinta ei juuri nyt toimi, yritä myöhemmin uudelleen (503)', 503
