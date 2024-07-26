"""
This module provides routes and functionality for a Flask web application.

It includes routes for loading data, rendering pages, booking, and purchasing places,
as well as handling user interactions.
"""

import json
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for


def load_clubs():
    """Load clubs from the JSON file."""
    with open("clubs.json", encoding="utf-8") as c:
        clubs_list = json.load(c)["clubs"]
    return clubs_list


def load_competitions():
    """Load and sort competitions from the JSON file."""

    date_format = "%Y-%m-%d %H:%M:%S"
    now = datetime.now()
    with open("competitions.json", encoding="utf-8") as comps:
        competitions_list = json.load(comps)["competitions"]

        for competition in competitions_list:
            # Parse the competition date string into a datetime object
            competition["date"] = datetime.strptime(competition["date"], date_format)

            # If the competition date is passed, it can't be booked.
            if competition["date"] < now:
                competition["canBeBooked"] = False
            else:
                competition["canBeBooked"] = True

        # Sort competitions by date(most recent first)
        competitions_list_sorted = sorted(competitions_list, key=lambda comp: comp["date"], reverse=True)

    return competitions_list_sorted


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

        now = datetime.now()
        for competition in competitions:

            # If the competition date is passed, it can't be booked.
            if competition["date"] < now:
                competition["canBeBooked"] = False
            else:
                competition["canBeBooked"] = True

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
    competition_name = request.form["competition"]
    club_name = request.form["club"]
    places_required = int(request.form["places"])

    # Find the competition and club based on the names
    competition = next((c for c in competitions if c["name"] == competition_name), None)
    club = next((c for c in clubs if c["name"] == club_name), None)

    # Initialize 'clubBookings' for the competition if not present
    if "clubBookings" not in competition:
        competition["clubBookings"] = {}

        # Initialize the club's booking count for this competition.
        competition["clubBookings"][club_name] = 0

    # Check if the total places booked by the club for this competition exceeds the allowed maximum
    if competition["clubBookings"][club_name] + places_required > 12:
        flash("You cannot book more than 12 places per competition.", category=competition_name)
    elif places_required > int(club["points"]):
        flash("You cannot redeem more points than you have available.", category=competition_name)
    elif places_required > int(competition["numberOfPlaces"]):
        flash("Not enough places available in the competition.", category=competition_name)
    else:
        # Deduct the points and update the number of places
        club["points"] = int(club["points"]) - places_required
        competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
        competition["clubBookings"][club_name] += places_required
        flash("Great - booking complete.", category=competition_name)

    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/logout")
def logout():
    """Log out and redirect to the index page."""
    return redirect(url_for("index"))


# TODO: Add route for points display
