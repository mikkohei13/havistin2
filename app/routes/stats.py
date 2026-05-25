from flask import Blueprint, render_template

from app.decorators import robust_cached

import stats.observers_species

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("/observers/species")
@stats_bp.route("/observers/species/")
@robust_cached(timeout=1)
def observers_species():
    html = stats.observers_species.main()
    return render_template("stats_observers_species.html", html=html)
