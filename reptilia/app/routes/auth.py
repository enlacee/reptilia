from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_raw_jwt, get_jti

from app.routes import api
from app.models.User import User
from app.models.Token import Token
from app.models.Entity import Entity
from app.models.Module import Module

from app.utils.handlers import exception_handler

@api.route('/login', methods= ['POST'])
@exception_handler
def login():
    data = {
        'status': False
    }

    username = request.json.get('username')
    password = request.json.get('password')

    if username and password:
        with User() as user:
            data['status'], data['access_token'], row_id = user.login_user(username, password)

        if data['status']:
            with Token() as token:
                token.insert(get_jti(data['access_token']), data['access_token'], row_id)

            with Entity() as entity:
                data['entity_prefix'] = entity.by_user(row_id)[0].get('prefix')

    return jsonify(data)

@api.route('/register', methods= ['POST'])
@exception_handler
def register():
    data = {
        'status': False
    }

    username = request.json.get('username')
    password = request.json.get('password')
    role_id = request.json.get('role_id')

    if username and password and role_id:
        with User() as user:
            data['status'] = user.register_user(username, password, role_id)

    return jsonify(data)

@api.route('/logout', methods= ['POST'])
@jwt_required
@exception_handler
def logout():
    data = {
        'status': False
    }
    jti = get_raw_jwt()['jti']

    with Token() as token:
        token.remove(jti)
        data['status'] = True

    return jsonify(data)

@api.route('/validate', methods = ['POST'])
@jwt_required
def validate():
    data = {
        'status': True,
        'new_route': False
    }

    name = request.json.get('name')
    module = request.json.get('module')

    jti = get_raw_jwt()['jti']

    with Token() as token:
        row = token.by_jti(jti)

    with Module() as _module:
        modules = _module.by_user(row.get('user_id'))
        modules = [m.get('route_name') for m in modules]
        if module is None or module not in modules:
            data['new_route'] = True
            data['route_name'] = modules[0]

    return jsonify(data)
