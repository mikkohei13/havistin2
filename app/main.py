from flask import Flask, render_template
from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import sys

import atlas.atlas
import atlas.squareform

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
@cache.cached()
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
def square(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    return render_template("squareform.html", html=html)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return 'Virhe tai sivua ei löydy (404)', 404
