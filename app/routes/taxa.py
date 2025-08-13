from flask import Blueprint, render_template, request
from flask_caching import Cache
from decorators import robust_cached

import taxa.taxa
import taxa.specieslist
import taxa.species
import taxa.new
import taxa.common_photos
import taxa.compare_years
import taxa.miss

taxa_bp = Blueprint('taxa', __name__)

@taxa_bp.route("/taxa/<string:taxon_id_untrusted>")
@robust_cached(timeout=86400) # 86400 = 24 h
def taxa_specieslist(taxon_id_untrusted):
    html = taxa.specieslist.main(taxon_id_untrusted)
    return render_template("taxa_specieslist.html", html=html)

@taxa_bp.route("/taxa")
@taxa_bp.route("/taxa/")
@robust_cached(timeout=10800) # 10800 = 3 h
def taxa_root():
    html = taxa.taxa.main()
    return render_template("taxa.html", html=html)

@taxa_bp.route("/taxa/species/<string:taxon_id_untrusted>")
@robust_cached(timeout=86400) # 86400 = 24 h
def taxa_species(taxon_id_untrusted):
    html = taxa.species.main(taxon_id_untrusted)
    return render_template("taxa_species.html", html=html)

@taxa_bp.route("/taxa/id/<string:page_name_untrusted>")
@robust_cached(timeout=86400)
def taxa_new(page_name_untrusted):
    html = taxa.new.main(page_name_untrusted)
    return render_template("taxa_new.html", html=html)

@taxa_bp.route("/taxa/photos_data/<string:taxon_id_untrusted>")
@robust_cached(timeout=10800)
def taxa_photos_data(taxon_id_untrusted):
    html = taxa.common_photos.main(taxon_id_untrusted)
    return render_template("taxa_photos_data.html", html=html)

@taxa_bp.route("/taxa/compare_years/<string:taxon_id_untrusted>")
@robust_cached(timeout=1) # 10800
def taxa_compare_years(taxon_id_untrusted):
    html = taxa.compare_years.main(taxon_id_untrusted)
    return render_template("taxa_compare_years.html", html=html)

@taxa_bp.route("/taxa/miss")
@robust_cached(timeout=1)
def taxa_miss():
    lat_untrusted = request.args.get('lat')
    lon_untrusted = request.args.get('lon')
    taxon_untrusted = request.args.get('taxon')
    since_year_untrusted = request.args.get('since_year', 2000)
    near_km_untrusted = request.args.get('near', 50)
    far_km_untrusted = request.args.get('far', 100)
    html = taxa.miss.main(lat_untrusted, lon_untrusted, taxon_untrusted, since_year_untrusted, near_km_untrusted, far_km_untrusted)
    return render_template("taxa_miss.html", html=html) 