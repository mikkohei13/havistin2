from flask import Blueprint, render_template
from flask_caching import Cache
from app.decorators import robust_cached

import info.info
import info.rain
import info.tower
import info.birds
import info.news
import info.river
import info.radar

# Create blueprint with url_prefix='/info'
info_bp = Blueprint('info', __name__, url_prefix='/info')

@info_bp.route('')  # This becomes /info
def info_root():
    html = info.info.main()
    return render_template("info.html", html=html)

@info_bp.route('/rain')
@robust_cached(timeout=150)  # 150 = 2½ min
def rain():
    html = info.rain.main()
    return render_template("info_rain.html", html=html)

@info_bp.route('/tower')
@robust_cached(timeout=150)
def tower():
    html = info.tower.main()
    return render_template("info_tower.html", html=html)

@info_bp.route('/birds/<string:secret>')
@robust_cached(timeout=3600)  # 3600 = 1 h
def birds(secret=''):
    html = info.birds.main(secret)
    return render_template("info_birds.html", html=html)

@info_bp.route('/news')
@robust_cached(timeout=10800)  # 10800 = 3h
def news():
    html = info.news.main()
    return render_template("info_news.html", html=html) 

@info_bp.route('/river')
@robust_cached(timeout=1)  # 10800 = 3h
def river():
    html = info.river.main()
    return render_template("info_river.html", html=html)

@info_bp.route('/radar')
@robust_cached(timeout=1)
def radar():
    html = info.radar.main()
    return render_template("info_radar.html", html=html)
