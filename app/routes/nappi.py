from flask import Blueprint, redirect, render_template, session

nappi_bp = Blueprint("nappi", __name__, url_prefix="/nappi")


@nappi_bp.route("")
@nappi_bp.route("/")
def nappi_root():
    user_data = session.get("user_data")
    if user_data is None or "errorCode" in user_data:
        return redirect("/login/start")
    return render_template("nappi.html")

