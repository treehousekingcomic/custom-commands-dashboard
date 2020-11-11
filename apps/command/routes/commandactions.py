from flask import (
    request,
    redirect,
    url_for,
    current_app,
    render_template,
    make_response,
)
from flask_discord import requires_authorization
from .. import command
import json
import psycopg2
from ...helpers import get_basic_data, get_role, get_roles, get_variables


@command.route("/server/<int:server_id>/command/delete", methods=["GET", "POST"])
@requires_authorization
def delete_command(server_id):
    if request.method == "GET":
        return redirect(url_for("main.manage_server", server_id=server_id))

    if request.method == "POST":
        data = json.loads(request.data)
        command_id = data["id"]

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM commands WHERE id = %s and guild = %s",
                    (int(command_id), server_id),
                )
                cmd = db.fetchone()

        if not cmd:
            return {
                "error": {"message": f"This command doesn't exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute("DELETE FROM commands WHERE id=%s", (cmd[0],))
                    conn.commit()

            return {"error": None, "data": {"message": "Command deleted successfully"}}


@command.route("/server/<int:server_id>/command/unapprove", methods=["GET", "POST"])
@requires_authorization
def unapprove_command(server_id):
    if request.method == "GET":
        return redirect(url_for("main.manage_server", server_id=server_id))

    if request.method == "POST":
        data = json.loads(request.data)
        command_id = data["id"]

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM commands WHERE id = %s and guild = %s",
                    (int(command_id), server_id),
                )
                cmd = db.fetchone()

        if not cmd:
            return {
                "error": {"message": f"This command doesn't exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "UPDATE commands SET approved = %s WHERE id = %s and guild = %s",
                        ("no", cmd[0], server_id),
                    )
                    conn.commit()

            return {"error": None, "data": {"message": "Command unapproved"}}


@command.route("/server/<int:server_id>/command/approve", methods=["GET", "POST"])
@requires_authorization
def approve_command(server_id):
    if request.method == "GET":
        return redirect(url_for("main.manage_server", server_id=server_id))

    if request.method == "POST":
        data = json.loads(request.data)
        command_id = data["id"]

        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM commands WHERE id = %s and guild = %s",
                    (int(command_id), server_id),
                )
                cmd = db.fetchone()

        if not cmd:
            return {
                "error": {"message": f"This command doesn't exists"},
                "data": None,
            }
        else:
            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute(
                        "UPDATE commands SET approved = %s WHERE id = %s and guild = %s",
                        ("yes", cmd[0], server_id),
                    )
                    conn.commit()

            return {"error": None, "data": {"message": "Command approved"}}


@command.route("/server/<int:server_id>/command/<int:command_id>")
@requires_authorization
def view_command(server_id, command_id):
    guild_ids, data, server = get_basic_data(server_id)
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute(
                "SELECT * FROM commands WHERE id = %s and guild = %s",
                (int(command_id), server_id),
            )
            cmd = db.fetchone()

    if not cmd:
        return redirect(url_for("main.servers"))

    # (11798, 696939596667158579, 700374484955299900, 'serverinfo', 'embed', None, 'yes')
    command_type = cmd[4]
    command_id = cmd[0]
    command_name = cmd[3]

    if command_type == "embed":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM embed WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

    if command_type == "text":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM text WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

    if command_type == "role":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM role WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

    if command_type == "random":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM randomtext WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

    if command_type == "mrl":
        command_type = "give and remove"
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM multirole WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

    template = render_template(
        "app/command/viewcommand.html",
        server=server,
        command_name=command_name,
        current_app=current_app,
        command_type=command_type,
        cmd_info=cmd_info,
        get_role=get_role,
    )
    response = make_response(template)
    return response


@command.route(
    "/server/<int:server_id>/command/<int:command_id>/edit", methods=["GET", "POST"]
)
def edit_command(server_id, command_id):
    guild_ids, data, server = get_basic_data(server_id)
    variables = get_variables(server_id)
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute(
                "SELECT * FROM commands WHERE id = %s and guild = %s",
                (int(command_id), server_id),
            )
            cmd = db.fetchone()

    if not cmd:
        return redirect(url_for("main.servers"))

    # (11798, 696939596667158579, 700374484955299900, 'serverinfo', 'embed', None, 'yes')
    command_type = cmd[4]
    command_id = cmd[0]
    command_name = cmd[3]

    if cmd[1] != current_app.discord.user_id:
        template = render_template("error/access-denied.html", current_app=current_app)
        response = make_response(template)
        return response

    if command_type == "text":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM text WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

        template = render_template(
            "app/command/edit/text.html",
            server=server,
            command_name=command_name,
            current_app=current_app,
            cmd_info=cmd_info,
            variables=variables,
        )
        return make_response(template)

    if command_type == "embed":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM embed WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()

        template = render_template(
            "app/command/edit/embed.html",
            server=server,
            command_name=command_name,
            current_app=current_app,
            cmd_info=cmd_info,
            variables=variables,
        )
        return make_response(template)

    if command_type == "role":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM role WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()
        roles = get_roles(server_id)
        template = render_template(
            "app/command/edit/singlerole.html",
            server=server,
            command_name=command_name,
            current_app=current_app,
            cmd_info=cmd_info,
            roles=roles,
            variables=variables,
        )
        return make_response(template)

    if command_type == "mrl":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM multirole WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()
        roles = get_roles(server_id)
        template = render_template(
            "app/command/edit/multirole.html",
            server=server,
            command_name=command_name,
            current_app=current_app,
            cmd_info=cmd_info,
            roles=roles,
            variables=variables,
        )
        return make_response(template)

    if command_type == "random":
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM randomtext WHERE command_id = %s",
                    (command_id,),
                )
                cmd_info = db.fetchone()
        template = render_template(
            "app/command/edit/random.html",
            server=server,
            command_name=command_name,
            current_app=current_app,
            cmd_info=cmd_info,
            variables=variables,
        )
        return make_response(template)
