from flask import Flask
import test
import sys

import atlas.main

app = Flask(__name__)

print("-------------- BEGIN -------------- -------------- --------------", file = sys.stdout)


@app.route("/")
def root():
    return atlas.main.main("Hoi!")

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="localhost", debug=True, port=80)
#    app.run()

