import math
from flask import current_app, render_template
import psycopg2


def create_paginator(current_page, per_page, results):
    pages = math.ceil(len(results) / per_page)
    if current_page <= 1:
        prev_link = None
    else:
        prev_link = current_page - 1
    if current_page >= pages:
        next_link = None
    else:
        next_link = current_page + 1

    links = [n for n in range(1, pages + 1)]
    if len(links) <= 1:
        links = None

    paginator = {
        "prev_link": prev_link,
        "next_link": next_link,
        "links": links,
        "page": current_page,
    }
    return paginator


def get_guilds():
    all_guilds = current_app.discord.fetch_guilds()
    guilds = [g for g in all_guilds if g.permissions.administrator]
    guild_ids = [g.id for g in all_guilds if g.permissions.administrator]

    return [guilds, guild_ids]


def get_data(guilds, server_id):
    data = []

    for s in guilds:
        if s.id == server_id:
            params = {
                "host": "localhost",
                "database": "ccbeta",
                "user": "shah",
                "password": "shah",
            }

            with psycopg2.connect(**params) as conn:
                with conn.cursor() as db:
                    db.execute("SELECT * FROM guild_data WHERE guild = %s", (s.id,))
                    data = db.fetchone()

    return data


def get_roles(server_id):
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute("SELECT * FROM roles WHERE guild = %s", (server_id,))
            data = db.fetchall()

    return data


def get_guild(guilds, server_id):
    for s in guilds:
        if s.id == server_id:
            server = s
            return server

    return None


def get_basic_data(server_id):
    guilds, guild_ids = get_guilds()
    data = get_data(guilds, server_id)
    server = get_guild(guilds, server_id)

    return [guild_ids, data, server]


def get_db():
    return [current_app.config["DB"], current_app.config["CONN"]]


def get_template(
    server_id, guild_ids, server, data, template_name, variables=None, roles=None
):
    if server_id not in guild_ids or not server:
        template = render_template(
            "error/server-not-found.html", current_app=current_app
        )

    elif not data:
        template = render_template("error/bot-not-found.html", current_app=current_app)
    else:
        template = render_template(
            f"{template_name}.html",
            current_app=current_app,
            server=server,
            variables=variables,
            roles=roles,
        )

    return template


def get_variables(server_id):
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute("SELECT * FROM variables WHERE guild = %s", (server_id,))
            variables = db.fetchall()

    return variables


def get_command_count(server_id):
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute("SELECT * FROM commands WHERE guild = %s", (server_id,))
            commands = db.fetchall()

    return len(commands)


def get_var_count(server_id):
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute("SELECT * FROM variables WHERE guild = %s", (server_id,))
            variables = db.fetchall()

    return len(variables)


def get_role(role_id):
    params = {
        "host": "localhost",
        "database": "ccbeta",
        "user": "shah",
        "password": "shah",
    }

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as db:
            db.execute("SELECT * FROM roles WHERE role = %s", (role_id,))
            data = db.fetchone()

    return data[2]
