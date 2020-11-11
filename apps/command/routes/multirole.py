from flask import make_response, current_app, request
from flask_discord import requires_authorization
from .. import command
from ...helpers import get_basic_data, get_template, get_variables, get_roles
import json
import psycopg2


@command.route("/server/<int:server_id>/multirole/edit", methods=["POST", "GET"])
@requires_authorization
def edit_multirole(server_id):
    guild_ids, data, server = get_basic_data(server_id)
    roles = get_roles(server_id)
    template = None
    variables = get_variables(server_id)

    if request.method == "GET":
        template = get_template(
            server_id,
            guild_ids,
            server,
            data,
            template_name="app/command/giverole",
            variables=variables,
            roles=roles,
        )

    if request.method == "POST":
        data = json.loads(request.data)
        command_name = data["name"].replace(" ", "")
        gives = data["gives"]
        removes = data["removes"]
        command_id = data["id"]

        if not command_name or not gives or not removes:
            return {
                "error": {"message": f"Invalid data passed"},
                "data": None,
            }

        from .config import reserved_words

        for word in reserved_words:
            if command_name.startswith(word) or word + " " in command_name:
                return {
                    "error": {"message": f"Command name contains reserved word."},
                    "data": None,
                }

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM commands WHERE name = %s and guild = %s",
                    (command_name, server_id),
                )
                cmd = db.fetchone()

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM aliases WHERE name = %s and guild = %s",
                    (command_name, server_id),
                )
                cmd2 = db.fetchone()

        if cmd and command_id != cmd[0] or cmd2:
            return {
                "error": {"message": f"Command {command_name} exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "UPDATE commands SET name = %s WHERE id = %s",
                        (command_name, command_id),
                    )
                    conn.commit()

            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "UPDATE multirole SET gives = %s::bigint[], removes = %s::bigint[] WHERE command_id = %s",
                        (gives, removes, command_id),
                    )

                    conn.commit()

            return {"error": None, "data": {"message": "Command updated"}}

    response = make_response(template)
    return response
