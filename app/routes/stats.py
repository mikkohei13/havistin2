from flask import Blueprint, render_template

from app.decorators import robust_cached

import stats.observers_species

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


def _render_observers_species(year_untrusted=None):
    html = stats.observers_species.main(year_untrusted=year_untrusted)
    return render_template("stats_observers_species.html", html=html)


@stats_bp.route("/observers/species")
@stats_bp.route("/observers/species/")
@robust_cached(timeout=1) # 72000 = 20 h
def observers_species():
    return _render_observers_species(year_untrusted=None)


@stats_bp.route("/observers/species/<int:year_untrusted>")
@stats_bp.route("/observers/species/<int:year_untrusted>/")
@robust_cached(timeout=1) # 72000 = 20 h
def observers_species_year(year_untrusted):
    return _render_observers_species(year_untrusted=year_untrusted)

