from flask import Blueprint
from werkzeug.local import LocalProxy
from flask import current_app

logger = LocalProxy(lambda: current_app.logger)

main = Blueprint('main', __name__)

from . import views
