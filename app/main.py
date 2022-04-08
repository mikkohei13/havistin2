from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

import sys

import atlas.atlas
import atlas.squareform

#import app_secrets

app = Flask(__name__)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)

@app.route("/")
def root():
    html = atlas.atlas.main()
    return render_template("index.html", html=html)

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
def square(square_id_untrusted, show_untrusted):
    html = atlas.squareform.main(square_id_untrusted, show_untrusted)
    return render_template("squareform.html", html=html)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return 'Virhe tai sivua ei löydy (404)', 404
