from flask import Blueprint, render_template, jsonify, request
from ..models.Token import Token

import requests
import logging

ui = Blueprint('routes', __name__)
api = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

@ui.route('/', defaults={'path': ''})
@ui.route('/<path:path>')
def render_vue(path):
    try:
        base_url = request.base_url

        with Token() as _token:
            tokens = _token.get_all()
            for token in tokens:
                headers = {
                    'Authorization': f"Bearer {token.get('token')}"
                }
                requests.post(f'{base_url}api/validate', headers=headers)

    except Exception as e:
        logger.error(f':{render_vue.__name__}: {e}')

    return render_template("index.html")


import app.routes.auth
import app.routes.list
import app.routes.charge
import app.routes.entities
import app.routes.user
import app.routes.carrier
import app.routes.agents
import app.routes.report
import app.routes.channel
import app.routes.modules
