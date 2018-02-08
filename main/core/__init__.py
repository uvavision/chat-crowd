from flask import Blueprint
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

main = Blueprint('main', __name__)

from . import routes, events, data, utils, const
