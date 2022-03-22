from flask import Flask, render_template
import sys

import atlas.main

app = Flask(__name__)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)


@app.route("/")
def root():
    body_content = atlas.main.main("Hoi!")
    return render_template("index.html", body_content=body_content)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="localhost", debug=True, port=80)
#    app.run()

