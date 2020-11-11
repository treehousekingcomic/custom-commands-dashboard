from flask import Flask
from config import config
from .main import main as main_blp
from .command import command as command_blp
from flask_discord import DiscordOAuth2Session, requires_authorization

discord_oauth = DiscordOAuth2Session()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
    discord_oauth.init_app(app)
    app.register_blueprint(main_blp)
    app.register_blueprint(command_blp)

    return app
