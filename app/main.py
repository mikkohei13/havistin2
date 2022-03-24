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
    square_id = request.args.get("id", default="", type=str)
    body_content = atlas.square.main(square_id)
    return render_template("square.html", body_content=body_content)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="localhost", debug=True, port=80)
#    app.run()

