from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
import json
import os

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to app folder
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_TEMPLATE = os.path.join(APP_ROOT, 'templates')
APP_DATA = os.path.join(APP_ROOT, 'data')
APP_DOMAIN = os.path.join(APP_ROOT, 'domains')

# kubernete = 'http://173.193.99.224:30310'
# local_url = 'http://0.0.0.0:7004'
# MTS_API_URL = local_url
# N_PER_AGENT = 3

'''
http://localhost:8080/login?role=agent&task_id=test123&workerid=test123&username=Jason&mode=mts&debug=1
'''


config = None
with open(path.join(APP_DOMAIN, 'app-activate.json'), 'r') as f:
    config = json.load(f)
uri_local = 'mongodb://localhost'
uri_remote = (config['compose-for-mongodb'][0]['credentials']['uri'] +
              '&ssl_cert_reqs=CERT_NONE')
cli = MongoClient(uri_remote)
mockdb = config["domain-db"]["db-name"]
COLL_NAME = config["domain-db"]["coll_domain_data"]
coll_data = cli[mockdb][COLL_NAME]
coll_chat = cli[mockdb][config["domain-db"]["coll_chat_data"]]
coll_chat_test = cli[mockdb][config["domain-db"]["coll_chat_data_test"]]
coll_crowd = cli[mockdb][config["domain-db"]["coll_cf_data"]]
coll_crowd_test = cli[mockdb][config["domain-db"]["coll_cf_data_test"]]
coll_coco_anno = cli[mockdb][config["domain-db"]["coll_coco_anno"]]
coll_coco_anno_test = cli[mockdb][config["domain-db"]["coll_coco_anno_test"]]

MTS_API_URL = config["mts-api"]["mts-endpoint"]
MTS_API_CID = config["mts-api"]["mts-api-cid"]
MTS_API_CONTEXT = config["mts-api"]["mts-api-context"]
MTS_API_MESSAGE = config["mts-api"]["mts-api-message"]
MTS_API_KB = config["mts-api"]["mts-api-kb"]

APP_URL = config["app-url"]
DOMAIN = config["domain-name"]
LST_META = config["metadata"]["LST_META"]
SORTING_KEY = config["metadata"]["SORTING_KEY"]
SORTING_ORDER = config["metadata"]["SORTING_ORDER"]
TEXT4DEBUG = config["metadata"]["TEXT4DEBUG"]
socketio = SocketIO()

CHAT_HTML = DOMAIN + '.chat.html'
VIZ_DATA_JSON = APP_STATIC + '/data/data-kbv.json'


def get_crowd_db(is_debug=True):
    if is_debug:
        return coll_crowd_test
    return coll_crowd


def get_chat_db(is_debug=True):
    if is_debug:
        return coll_chat_test
    return coll_chat

def get_coco_anno_db(is_debug=True):
    if is_debug:
        return coll_coco_anno_test
    return coll_coco_anno


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'RAWEFAwW#$Q$'

    from .core import main as main_blueprint
    # from .viz.kbv import gen_visual_data
    # gen_visual_data()
    app.register_blueprint(main_blueprint)
    socketio.init_app(app)
    return app
