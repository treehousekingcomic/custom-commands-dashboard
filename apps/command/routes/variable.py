from flask import make_response, current_app, request
from flask_discord import requires_authorization
from .. import command
from ...helpers import get_basic_data, get_db, get_template, get_variables
import json
import psycopg2


@command.route("/server/<int:server_id>/variables", methods=["GET", "POST"])
@requires_authorization
def variable_view(server_id):
    guild_ids, data, server = get_basic_data(server_id)
    template = None

    variables = get_variables(server_id)

    if request.method == "GET":
        template = get_template(
            server_id,
            guild_ids,
            server,
            data,
            template_name="app/command/variable",
            variables=variables,
        )

    if request.method == "POST":
        data = json.loads(request.data)
        variable_name = data["name"]
        variable_value = data["value"]

        if not variable_name or not variable_value:
            return {
                "error": {"message": f"Invalid data passed"},
                "data": None,
            }

        if not variable_name.endswith("}"):
            variable_name = variable_name + "}"

        if not variable_name.startswith("{"):
            variable_name = "{" + variable_name

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM variables WHERE name = %s and guild = %s",
                    (variable_name, server_id),
                )
                variable = db.fetchone()

        if variable:
            return {
                "error": {"message": f"Variable {variable_name} already exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "INSERT INTO variables (name, value, guild, userid) VALUES (%s, %s, %s, %s)",
                        (
                            variable_name,
                            variable_value,
                            server_id,
                            current_app.discord.user_id,
                        ),
                    )
                    conn.commit()

            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "SELECT * FROM variables WHERE name = %s and guild = %s",
                        (variable_name, server_id),
                    )
                    variable = db.fetchone()

            return {
                "error": None,
                "data": {"message": "Variable created", "variable_id": variable[0]},
            }

    response = make_response(template)
    return response


@command.route("/server/<int:server_id>/variables/delete", methods=["POST"])
@requires_authorization
def delete_variable(server_id):
    data = json.loads(request.data)
    var_id = data["id"]
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute(
                "DELETE FROM variables WHERE id = %s and guild = %s",
                (var_id, server_id),
            )
            conn.commit()

    return {"error": None, "data": {"message": "Variable deleted"}}
