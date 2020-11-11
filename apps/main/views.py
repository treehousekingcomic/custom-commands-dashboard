from flask import render_template, make_response, current_app, redirect, url_for
from flask_discord import requires_authorization
from . import main
from ..helpers import get_data, get_guilds, get_guild, get_command_count, get_var_count
import psycopg2


@main.route("/")
def index():
    template = render_template("app/index.html", current_app=current_app)
    response = make_response(template)
    return response


@main.route("/servers/")
@requires_authorization
def servers():
    guilds, guild_ids = get_guilds()

    data = []
    gdata = []
    for guild in guilds:
        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute("SELECT * FROM guild_data WHERE guild = %s", (guild.id,))
                gdata = [db.fetchone(), guild]

        command_count = get_command_count(guild.id)
        var_count = get_var_count(guild.id)
        gdata.append(command_count)
        gdata.append(var_count)

        data.append(gdata)

    _in = []
    out = []

    for d in data:
        if d[0]:
            _in.append(d)
        else:
            out.append(d)

    data = _in + out

    template = render_template(
        "app/servers.html", current_app=current_app, servers=data
    )
    response = make_response(template)
    return response


@main.route("/server/<int:server_id>")
@requires_authorization
def manage_server(server_id):
    guilds, guild_ids = get_guilds()
    server = get_guild(guilds, server_id)
    data = get_data(guilds, server_id)

    if server_id not in guild_ids or not server:
        template = render_template(
            "error/server-not-found.html", current_app=current_app
        )

    elif not data:
        template = render_template("error/bot-not-found.html", current_app=current_app)
    else:
        params = {
            "host": "localhost",
            "database": "ccbeta",
            "user": "shah",
            "password": "shah",
        }

        with psycopg2.connect(**params) as conn:
            with conn.cursor() as db:
                db.execute(
                    "SELECT * FROM commands WHERE guild = %s ORDER BY name ASC",
                    (server.id,),
                )
                commands = db.fetchall()

        template = render_template(
            "app/command/commands.html",
            current_app=current_app,
            server=server,
            commands=commands,
        )

    response = make_response(template)
    return response


@main.route("/invite-bot/<int:server_id>")
def invite_bot(server_id):
    if server_id:
        return current_app.discord.create_session(
            scope=["bot"],
            permissions=335931488,
            guild_id=server_id,
            disable_guild_select=True,
        )
    else:
        return current_app.discord.create_session(scope=["bot"], permissions=335931488)


@main.route("/login-view/")
def login_view():
    template = render_template("app/login.html", current_app=current_app)
    response = make_response(template)
    return response


@main.route("/login/")
def login():
    return current_app.discord.create_session(scope=["identify", "guilds"])


@main.route("/callback/")
def callback():
    data = current_app.discord.callback()
    redirect_to = data.get("redirect", "/servers/")
    return redirect(redirect_to)


@main.route("/logout/")
@requires_authorization
def logout():
    current_app.discord.revoke()
    template = render_template("app/logout.html", current_app=current_app)
    response = make_response(template)
    return response
