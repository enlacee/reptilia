from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.Carrier import Carrier

from app.utils.handlers import exception_handler

@api.route('/carriers', methods= ['POST'])
@jwt_required
@exception_handler
def list_carriers():
    data = {
        'status': True
    }

    with Carrier() as carrier:
        data['carriers'] = carrier.list_carriers()

    return jsonify(data)
