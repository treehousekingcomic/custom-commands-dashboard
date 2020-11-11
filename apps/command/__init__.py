from flask import Blueprint

command = Blueprint("command", __name__)

from . import views
from . import errors
