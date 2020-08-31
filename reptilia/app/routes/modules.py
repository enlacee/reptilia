from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_raw_jwt

from app.routes import api
from app.models.Token import Token
from app.models.Module import Module

from app.utils.handlers import exception_handler

@api.route('/get-modules', methods = ['POST'])
@jwt_required
@exception_handler
def get_modules():
    data = {
        'status': True
    }

    jti = get_raw_jwt()['jti']

    with Token() as token:
        user = token.by_jti(jti)

    if user:
        with Module() as module:
            data['modules'] = module.by_user(user.get('user_id'))

    return jsonify(data)
