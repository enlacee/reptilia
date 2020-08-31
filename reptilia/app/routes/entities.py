from flask import jsonify
from flask_jwt_extended import jwt_required, get_raw_jwt

from app.routes import api
from app.models.Entity import Entity
from app.models.Token import Token

from app.utils.handlers import exception_handler

@api.route('/entities', methods= ['POST'])
@jwt_required
@exception_handler
def entities():
    data = {
        'status': True
    }

    with Entity() as _entity:
        data['entities'] = _entity.get_all()

    return jsonify(data)

@api.route('/entities-user', methods= ['POST'])
@jwt_required
@exception_handler
def entities_by_user():
    data = {
        'status': True
    }

    jti = get_raw_jwt()['jti']

    with Token() as token:
        user = token.by_jti(jti)

    if user:
        with Entity() as _entity:
            data['entities'] = _entity.by_user(user.get('user_id'))

    return jsonify(data)

