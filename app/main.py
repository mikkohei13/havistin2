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
    body_content = atlas.main.main("Hoi")
    return render_template("index.html", body_content=body_content)

@app.route("/ruutulomake/<string:square_id_untrusted>/<string:show_untrusted>")
def square(square_id_untrusted, show_untrusted):
    html_table, html_title, html_heading, html_showselection, info_top, info_bottom = atlas.square.main(square_id_untrusted, show_untrusted)
    return render_template("square.html", html_title=html_title, html_table=html_table, html_heading=html_heading, html_showselection=html_showselection, info_top=info_top, info_bottom=info_bottom)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return 'Virhe tai sivua ei löydy (404)', 404


#if __name__ == "__main__":
    # Only for debugging while developing
#    app.run(host="localhost", debug=True, port=80)

    # For production
#    app.run()

