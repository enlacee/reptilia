from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.LoadClients import LoadClients, LoadClientsV2
from app.models.Charge import Charge
from app.models.List import List
from app.models.Channel import Channel

from app.utils.handlers import exception_handler

import pandas as pd
import math
import datetime
import time
import json
import logging

logger = logging.getLogger(__name__)

@api.route('/all-charges', methods= ['POST'])
@jwt_required
@exception_handler
def all_charges():
    data = {
        'status': True
    }

    with Charge() as _charge:
        data['charges'] = _charge.get_all()

    return jsonify(data)

@api.route('/carga', methods= ['POST'])
@jwt_required
@exception_handler
def charge_up():
    data = {
        'status': False,
        'msg': '',
    }

    try:
        list_id = request.form.get('list_id')
        file = list(request.files)
        iterations = request.form.get('iterations') if request.form.get('iterations') else 5
        seconds = request.form.get('seconds') if request.form.get('seconds') else 900
        carrier_id = request.form.get('carrier_id')
        channel_id = request.form.get('channel_id')
        entity_prefix = request.form.get('entity_prefix')
        matched_columns = request.form.get('matched_columns')
        matched_columns = json.loads(matched_columns)

        columns = {
            'code': matched_columns.get('code') if matched_columns.get('code') else 'codigo',
            'name': matched_columns.get('name') if matched_columns.get('name') else 'nombre',
            'product': matched_columns.get('product') if matched_columns.get('product') else 'producto',
            'amount': matched_columns.get('amount') if matched_columns.get('amount') else 'monto',
            'currency': matched_columns.get('currency') if matched_columns.get('currency') else 'moneda',
            'date': matched_columns.get('date') if matched_columns.get('date') else 'fecha',
            'phone': matched_columns.get('phone') if matched_columns.get('phone') else 'fono',
            'numero_asesor': 'numero_asesor',
            'asesor': 'asesor',
            'genre': 'genero',
            'account': 'cuenta',
        }

        start = time.time()

        if len(file) and entity_prefix:

            with Channel() as c:
                channel = c.by_id(channel_id)
                channel_name = channel.get('name').upper()
            if channel_name == 'SMS' or (channel_name == 'CALL' and list_id and carrier_id):
                name = file[0]
                _bytes = request.files[name]
                lines = pd.read_excel(_bytes, dtype = {f"{columns.get('code')}": str, f"{columns.get('currency')}": str})
                file_tmp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

                rows = []
                count_out = 0
                for index, row in lines.iterrows():
                    if pd.notna(row[columns.get('code')]):
                        rows.append(dict(row))
                    else:
                        count_out += 1

                db = entity_prefix
                db = 'mibanco' if 'mibanco' in db else db
                db = 'bbva' if 'bbva' in db else db
                db = 'movistar' if 'convergente' in db or 'movistar' in db else db
                print(db)

                with Charge() as charge:
                    row_id = charge.add_charge(list_id if channel_name == 'CALL' else 0, carrier_id if channel_name == 'CALL' else 0, iterations, seconds, entity_prefix, channel_id)

                if row_id:
                    loader = LoadClients(rows, db = db, list_id = list_id, charge_id = row_id, columns = columns, channel_name = channel_name)
                    report = loader.start()
                    loader.load_data()
                    # loader = LoadClientsV2(lines, db = db, list_id = list_id, charge_id = row_id, columns = columns, channel_name = channel_name)

                    minutes = (time.time() - start) / 60
                    seconds = int((minutes - int(minutes)) * 60)
                    minutes = int(minutes)

                    data['time'] = f'{minutes} min. {seconds} sec.'
                    data['status'] = True
                    data = {**data, **report}
                    data['count_out'] = data['count_out'] + count_out if data['count_out'] else count_out

                    if not data['msg']:
                        data['msg'] = 'Success!'
                    else:
                        data['status'] = False

    except Exception as e:
        data['msg'] = f'Error {e}'
        logger.error(e)

    return jsonify(data)

@api.route('/update-charge', methods= ['POST'])
@jwt_required
@exception_handler
def update_charge():
    data = {
        'status': True
    }

    charge_id = request.json.get('charge_id')
    carrier_id = request.json.get('carrier_id')

    with Charge() as _charge:
        _charge.update(charge_id, carrier_id)

    return data
