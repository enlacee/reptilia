from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.User import User
from app.utils.handlers import exception_handler

@api.route('/users', methods= ['POST'])
@jwt_required
@exception_handler
def get_users():
    data = {
        'status': True
    }

    with User() as user:
        data['users'] = user.get_users()

    return jsonify(data)

@api.route('/roles', methods= ['POST'])
@jwt_required
@exception_handler
def get_roles():
    data = {
        'status': True
    }

    with User() as user:
        data['roles'] = user.get_roles()

    return jsonify(data)
