from flask import Flask, render_template
from anaglyph_generator import create_anaglyph

app = Flask(__name__)

@app.route("/")
def map():
    return render_template("leaflet_map.html")

@app.route('/<string:coord>', methods=['POST'])
def anaglyph(coord):
    LatLng = coord.split("_")
    lat = LatLng[0]
    lng = LatLng[1]

    lat = float(lat)
    lng = float(lng)

    create_anaglyph(lat, lng)

    return render_template("anaglyph.html")

if __name__ == "__main__":
    app.run(debug=True)