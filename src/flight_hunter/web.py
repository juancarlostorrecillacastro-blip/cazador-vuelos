"""Panel local: enciende/apaga la busqueda automatica y muestra el historial de chollos."""

import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, url_for

from flight_hunter import automation_control, history

load_dotenv()

GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

app = Flask(__name__)
app.secret_key = "cazador-vuelos-local"


@app.route("/")
def index():
    state = automation_control.get_workflow_state(GITHUB_REPO, GITHUB_TOKEN)
    return render_template("index.html", is_active=(state == "active"))


@app.route("/toggle", methods=["POST"])
def toggle():
    state = automation_control.get_workflow_state(GITHUB_REPO, GITHUB_TOKEN)
    turning_on = state != "active"
    automation_control.set_workflow_enabled(GITHUB_REPO, GITHUB_TOKEN, enabled=turning_on)
    flash("Busqueda activada." if turning_on else "Busqueda desactivada.")
    return redirect(url_for("index"))


@app.route("/historial")
def historial():
    entries = history.fetch_remote_history(GITHUB_REPO)
    return render_template("history.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
