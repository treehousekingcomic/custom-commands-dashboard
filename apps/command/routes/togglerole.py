from flask import make_response, current_app, request
from flask_discord import requires_authorization
from .. import command
from ...helpers import get_basic_data, get_template, get_variables, get_roles
import json
import psycopg2


@command.route("/server/<int:server_id>/create/togglerole", methods=["POST", "GET"])
@requires_authorization
def create_togglerole(server_id):
    guild_ids, data, server = get_basic_data(server_id)
    template = None
    variables = get_variables(server_id)
    roles = get_roles(server_id)

    if request.method == "GET":
        template = get_template(
            server_id,
            guild_ids,
            server,
            data,
            template_name="app/command/togglerole",
            variables=variables,
            roles=roles,
        )

    if request.method == "POST":
        data = json.loads(request.data)
        command_name = data["name"].replace(" ", "")
        command_roles = data["roles"]

        if not command_name or not command_roles:
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

        if cmd or cmd2:
            return {
                "error": {"message": f"Command {command_name} exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:

                with conn.cursor() as db:
                    db.execute(
                        "INSERT INTO commands "
                        "(userid, guild, name, type, help, approved) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            current_app.discord.user_id,
                            server_id,
                            command_name,
                            "role",
                            None,
                            "yes",
                        ),
                    )
                    conn.commit()

            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "SELECT * FROM commands WHERE name = %s and guild = %s",
                        (command_name, server_id),
                    )
                    cmd = db.fetchone()

            cmd_id = cmd[0]

            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "INSERT INTO role (command_id, role, action) VALUES (%s::bigint, %s::bigint[], %s::text)",
                        (cmd_id, command_roles, "toggle"),
                    )

                    conn.commit()

            return {"error": None, "data": {"message": "Command created"}}

    response = make_response(template)
    return response
