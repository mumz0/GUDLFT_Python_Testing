"""
This module provides routes and functionality for a Flask web application.

It includes routes for loading data, rendering pages, booking, and purchasing places,
as well as handling user interactions.
"""

import json

from flask import Flask, flash, redirect, render_template, request, url_for


def load_clubs():
    """Load clubs from the JSON file."""
    with open("clubs.json", encoding="utf-8") as c:
        clubs_list = json.load(c)["clubs"]
    return clubs_list


def load_competitions():
    """Load competitions from the JSON file."""
    with open("competitions.json", encoding="utf-8") as comps:
        competitions_list = json.load(comps)["competitions"]
    return competitions_list


app = Flask(__name__)
app.secret_key = "something_special"

competitions = load_competitions()
clubs = load_clubs()


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")


@app.route("/show_summary", methods=["POST"])
def show_summary():
    """
    Render the summary page for a specific club based on email.

    This function retrieves a club based on the provided email from the form data.
    If the email is found, it renders the 'welcome.html' template with the club and competitions data.
    If the email is not found, it flashes an error message and redirects to the index page.

    Returns:
        str: Rendered HTML template.
    """
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
        return render_template("welcome.html", club=club, competitions=competitions)
    except IndexError:
        flash("Email does not exist.")
        return redirect("/")


@app.route("/book/<competition>/<club>")
def book(competition, club):
    """Render the booking page for a specific competition and club."""
    found_club = [c for c in clubs if c["name"] == club][0]
    found_competition = [c for c in competitions if c["name"] == competition][0]
    if found_club and found_competition:
        return render_template("booking.html", club=found_club, competition=found_competition)
    flash("Something went wrong - please try again.")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchase_places", methods=["POST"])
def purchase_places():
    """Handle the reservation of places for a specific competition and club."""
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    places_required = int(request.form["places"])
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    flash("Great - booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/logout")
def logout():
    """Log out and redirect to the index page."""
    return redirect(url_for("index"))


# TODO: Add route for points display
