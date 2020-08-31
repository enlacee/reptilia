from flask import Flask, render_template, jsonify
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from app.utils.fun import update_fun

from app.routes import api
from app.routes import ui

from app.models.Token import Token

import locale
import os
import logging

locale.setlocale(locale.LC_TIME, 'es_PE.UTF-8')

logging.basicConfig(filename='./rept.log', level=logging.INFO, format="%(name)s - [%(levelname)s] - %(asctime)s --- %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__, static_folder = "./static", template_folder = "./templates")

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_BLACKLIST_ENABLED'] = os.getenv('JWT_BLACKLIST_ENABLED')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))

app.register_blueprint(ui)
app.register_blueprint(api, url_prefix = '/api')

jwt = JWTManager(app)
cors = CORS(app, resources = {r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins = '*')

@jwt.token_in_blacklist_loader
def check_token(decrypted_token):
    try:
        jti = decrypted_token['jti']
        with Token() as token:
            return not token.token_exist(jti)

    except Exception as e:
        logger.error(f':{check_token.__name__}: {e}')

    return True

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    try:
        token_type = expired_token['type']
        jti = expired_token['jti']

        with Token() as token:
            token.remove(jti)

    except Exception as e:
        logger.error(f':{my_expired_token_callback.__name__}: {e}')

    return jsonify({
        'status': 401
    }), 401

@socketio.on('update')
def socket_update(data):
    try:
        logger.info(f':{socket_update.__name__}: {data}')
        key = data.get('key')
        r = update_fun(**data)
        emit('update-front', {**r, **data}, broadcast = True)
    except Exception as e:
        logger.error(f':{socket_update.__name__}: {e}')
