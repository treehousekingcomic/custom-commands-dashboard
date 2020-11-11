from flask import make_response, render_template, current_app, request
from flask_discord import requires_authorization
from . import command
from ..helpers import get_basic_data, get_template
from .routes import *
import psycopg2
import json


@command.route("/server/<int:server_id>/settings", methods=["POST", "GET"])
@requires_authorization
def edit_settings(server_id):
    guild_ids, data, server = get_basic_data(server_id)
    template = None
    if request.method == "GET":
        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute("SELECT * FROM guild_data WHERE guild = %s", (server_id,))
                data = db.fetchone()

        template = render_template(
            f"app/settings.html",
            current_app=current_app,
            server=server,
            variables=None,
            settings=data,
        )
    if request.method == "POST":
        data = json.loads(request.data)
        prefix = data["prefix"]
        cprefix = data["cprefix"] or None
        noprefix = data["noprefix"]

        if noprefix:
            noprefix = "yes"
        else:
            noprefix = "no"

        print(prefix, cprefix, noprefix)

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "UPDATE guild_data SET prefix = %s , cprefix = %s , noprefix = %s WHERE guild = %s",
                    (prefix, cprefix, noprefix, server_id),
                )
                conn.commit()

        return {"error": None, "data": {"message": "Settings updated"}}
    response = make_response(template)
    return response
