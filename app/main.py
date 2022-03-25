from flask import Flask, render_template, request
import sys

import atlas.main
import atlas.square

app = Flask(__name__)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)


@app.route("/")
def root():
    body_content = atlas.main.main("Hoi!")
    return render_template("index.html", body_content=body_content)

@app.route("/square", methods=['GET'])
def square():
    html_table, html_heading = atlas.square.main()
    return render_template("square.html", html_table=html_table, html_heading=html_heading)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="localhost", debug=True, port=80)
#    app.run()

