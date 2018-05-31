from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
import json
import os
from os import sys, path
import spacy
nlp_spacy = spacy.load('en_core_web_sm')
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to app folder
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_TEMPLATE = os.path.join(APP_ROOT, 'templates')
APP_DATA = os.path.join(APP_ROOT, 'data')
APP_DOMAIN = os.path.join(APP_ROOT, 'domains')
APP_GAZETTEER = os.path.join(APP_DATA, 'gazetteers')

add_bot_response = False

config = None
config_file = path.join(APP_DOMAIN, 'app-{}.json'.format(os.environ['domain']))
with open(config_file) as f:
    config = json.load(f)
uri_local = 'mongodb://localhost'
uri_remote = (config['compose-for-mongodb'][0]['credentials']['uri'] +
              '&ssl_cert_reqs=CERT_NONE')
cli = MongoClient(uri_remote)
mockdb = config["domain-db"]["db-name"]
COLL_NAME = config["domain-db"]["coll_domain_data"]
coll_data = cli[mockdb][COLL_NAME]
coll_chat = cli[mockdb][config["domain-db"]["coll_chat_data"]]
coll_chat_cache = cli[mockdb][config["domain-db"]["coll_chat_data_cache"]]
coll_cf_dispatch_semaphore = cli[mockdb][config["domain-db"]["coll_cf_dispatch_semaphore"]]
coll_chat_test = cli[mockdb][config["domain-db"]["coll_chat_data_test"]]
coll_crowd = cli[mockdb][config["domain-db"]["coll_cf_data"]]
coll_crowd_test = cli[mockdb][config["domain-db"]["coll_cf_data_test"]]
coll_anno = cli[mockdb][config["domain-db"]["coll_anno_data"]]


DOMAIN = config["domain-name"]

socketio = SocketIO()

# CHAT_HTML = 'vision-dialog.chat.{}.html'.format(os.environ['domain'])
CHAT_HTML = 'vision-dialog.chat.html'
TEST_HTML = 'test.html'
TEST_DATA_FILE = os.path.join(APP_DATA, 'quiz_data.json')


def get_crowd_db(is_debug=True):
    if is_debug:
        return coll_crowd_test
    return coll_crowd


def get_chat_db(is_debug=True):
    if is_debug:
        return coll_chat_test
    return coll_chat


def get_chat_cache_db():
    return coll_chat_cache


def get_anno_db(is_debug=True):
    return coll_anno


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'RAWEFAwW#$Q$'

    from .core import main as main_blueprint
    app.register_blueprint(main_blueprint)
    socketio.init_app(app)
    return app
