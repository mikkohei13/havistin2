from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

import sys

import atlas.main
import atlas.square

#import app_secrets

app = Flask(__name__)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)

@app.route("/")
def root():
    html = atlas.main.main()
    return render_template("index.html", html=html)

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
def square(square_id_untrusted, show_untrusted):
    html = atlas.square.main(square_id_untrusted, show_untrusted)
    return render_template("square.html", html=html)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return 'Virhe tai sivua ei löydy (404)', 404


#if __name__ == "__main__":
    # Only for debugging while developing
#    app.run(host="localhost", debug=True, port=80)

    # For production
#    app.run()

