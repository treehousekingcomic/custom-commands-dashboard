from . import main
from flask import redirect, url_for, render_template, make_response, current_app
import flask_discord
import requests


@main.app_errorhandler(404)
def page_not_found(e):
    return "Page Not found"


@main.app_errorhandler(flask_discord.exceptions.Unauthorized)
def not_logged_in(e):
    return redirect(url_for("main.login_view"))


@main.app_errorhandler(requests.exceptions.ConnectionError)
def connection_lost(e):
    return "connection lost"


@main.app_errorhandler(flask_discord.exceptions.AccessDenied)
def not_logged_in(e):
    template = render_template("error/access-denied.html", current_app=current_app)
    response = make_response(template)
    return response
