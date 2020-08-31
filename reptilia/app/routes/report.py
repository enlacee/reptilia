from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.Report import Report

from app.utils.handlers import exception_handler
from app.utils.fun import default

import datetime
import logging

logger = logging.getLogger(__name__)

@api.route('/report', methods= ['POST'])
@jwt_required
@exception_handler
def init_report():
    data = {
        'status': True
    }

    now = request.json.get('date')
    db = request.json.get('db')
    limit = request.json.get('limit', 0)

    now = datetime.datetime.strptime(now, '%d/%m/%Y').strftime('%Y-%m-%d')

    with Report(db, now) as _report:
        data['called_clients'] = len(_report.called_clients())
        data['total_calls'] = list(map(default, _report.get_all(limit)))
        data['contacted_clients'] = len(_report.contacted_clients())
        data['wrong_number'] = len(_report.wrong_number())
        data['all_clients'] = len(_report.all_clients())

    return jsonify(data)
