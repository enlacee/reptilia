from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.Channel import Channel

from app.utils.handlers import exception_handler

@api.route('/channels', methods= ['POST'])
@jwt_required
@exception_handler
def list_channels():
    data = {
        'status': True
    }

    with Channel() as channel:
        data['channels'] = channel.list_channels()

    return jsonify(data)
