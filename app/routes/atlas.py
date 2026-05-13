from flask import Blueprint, render_template, make_response
from flask_caching import Cache
from app.decorators import robust_cached
import requests
import app_secrets

import atlas.atlas
import atlas.here
import atlas.species
import atlas.specieslist
import atlas.singlespecies
import atlas.squares
import atlas.observers
import atlas.species_proportions
import atlas.completelists
import atlas.summap
import atlas.comparesquares

atlas_bp = Blueprint('atlas', __name__, url_prefix='/atlas')

@atlas_bp.route("")
@atlas_bp.route("/")
@robust_cached(timeout=120) # 120
def atlas_root():
    html = atlas.atlas.main()
    return render_template("atlas.html", html=html)

@atlas_bp.route("/havaintosuhteet")
@atlas_bp.route("/havaintosuhteet/")
@robust_cached(timeout=10800)
def species_proportions():
    html = atlas.species_proportions.main()
    return render_template("species_proportions.html", html=html)

@atlas_bp.route("/here/<string:square_id_untrusted>")
@robust_cached(timeout=3600)
def here(square_id_untrusted):
    html = atlas.here.main(square_id_untrusted)
    return render_template("atlas_here.html", html=html)
@atlas_bp.route("/lajiluettelo")
@atlas_bp.route("/lajiluettelo/")
@robust_cached(timeout=10800)
def atlas_specieslist():
    html = atlas.specieslist.main()
    return render_template("atlas_specieslist.html", html=html)

@atlas_bp.route("/laji/<string:species_name_untrusted>")
@robust_cached(timeout=86400) # 86400
def atlas_singlespecies(species_name_untrusted):
    html = atlas.singlespecies.main(species_name_untrusted)
    return render_template("atlas_singlespecies.html", html=html)

@atlas_bp.route("/lajit")
@atlas_bp.route("/lajit/")
@robust_cached(timeout=10800)
def atlas_species():
    html = atlas.species.main()
    return render_template("atlas_species.html", html=html)

@atlas_bp.route("/ruudut")
@atlas_bp.route("/ruudut/")
@robust_cached(timeout=10800)
def atlas_squares():
    html = atlas.squares.main()
    return render_template("atlas_squares.html", html=html)

@atlas_bp.route("/havainnoijat")
@atlas_bp.route("/havainnoijat/")
@robust_cached(timeout=10800)
def atlas_observers():
    html = atlas.observers.main()
    return render_template("atlas_observers.html", html=html)

@atlas_bp.route("/listat")
@atlas_bp.route("/listat/")
@robust_cached(timeout=10800)
def atlas_completelists():
    html = atlas.completelists.main()
    return render_template("atlas_completelists.html", html=html)

@atlas_bp.route("/luokka/<string:class_untrusted>")
@robust_cached(timeout=10800)
def atlas_summap(class_untrusted):
    html = atlas.summap.main(class_untrusted)
    return render_template("atlas_summap.html", html=html)

@atlas_bp.route("/ruutuvertailu/<string:society_untrusted>")
@robust_cached(timeout=43200) # 43200 = 12 h
def atlas_comparesquares(society_untrusted):
    html = atlas.comparesquares.main(society_untrusted)
    return render_template("atlas_comparesquares.html", html=html)
