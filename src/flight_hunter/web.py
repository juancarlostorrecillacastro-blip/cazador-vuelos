"""Formulario web local para gestionar las rutas vigiladas, sin editar YAML a mano."""

from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from flight_hunter import airports, route_manager

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "config.yaml"

app = Flask(__name__)
app.secret_key = "cazador-vuelos-local"  # solo protege mensajes flash en un servidor local


@app.route("/")
def index():
    routes = route_manager.load_routes(CONFIG_PATH)
    cities = airports.load_cities()
    return render_template("index.html", routes=routes, cities=cities)


@app.route("/routes", methods=["POST"])
def create_route():
    try:
        origin = route_manager.extract_iata_code(request.form["origin"])
        destination = route_manager.extract_iata_code(request.form["destination"])
        departure_month = route_manager.validate_month(request.form["departure_month"])
        return_month_raw = request.form.get("return_month") or ""

        route = {
            "origin": origin,
            "destination": destination,
            "max_price": float(request.form["max_price"]),
            "currency": request.form["currency"],
            "departure_month": departure_month,
        }
        if return_month_raw:
            route["return_month"] = route_manager.validate_month(return_month_raw)

        route_manager.add_route(CONFIG_PATH, route)
        flash(f"Ruta {origin} -> {destination} añadida.")
    except ValueError as error:
        flash(f"No se pudo añadir la ruta: {error}")

    return redirect(url_for("index"))


@app.route("/routes/<int:index>/delete", methods=["POST"])
def delete_route(index: int):
    route_manager.remove_route(CONFIG_PATH, index)
    flash("Ruta eliminada.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
