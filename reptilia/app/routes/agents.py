from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.routes import api
from app.models.RemoteAgents import RemoteAgents

from app.utils.handlers import exception_handler

@api.route('/remote-agents-list', methods= ['POST'])
@jwt_required
@exception_handler
def remote_agents_list():
    data = {
        'status': True
    }

    with RemoteAgents() as _agents:
        data['agents'] = _agents.get_all()

    return jsonify(data)

@api.route('/remote-agents-update-lines', methods= ['POST'])
@jwt_required
@exception_handler
def remote_agents_update_lines():
    data = {
        'status': True
    }

    lines = request.json.get('lines')
    _id = request.json.get('id')

    if lines:
        with RemoteAgents() as _agents:
            _agents.update_lines(_id, lines)
            data['status'] = True

    return jsonify(data)
