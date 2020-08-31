from app.models.Report import Report
import json
import datetime
import decimal
import logging

logger = logging.getLogger(__name__)

def default(row):
    for field, val in row.items():
        if isinstance(val, (datetime.datetime, datetime.date,)):
            row[field] = val.strftime('%Y/%m/%d %H:%M:%S')
        if isinstance(val, decimal.Decimal):
            row[field] = str(val)

    return row

def update_fun(key, db, limit = None, date = None):
    try:
        db = 'mibanco' if 'mibanco' in db else db
        db = 'bbva' if 'bbva' in db else db
        date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d') if date else datetime.datetime.now().strftime('%Y-%m-%d')

        with Report(db, date) as _report:
            data = {}
            if key == 'called_clients':
                data['rows'] = len(_report.called_clients())
            elif key == 'total_calls':
                data['rows'] = list(map(default, _report.get_all(limit)))
            elif key == 'contacted_clients':
                data['rows'] = len(_report.contacted_clients())
            elif key == 'wrong_number':
                data['rows'] = len(_report.wrong_number())
            elif key == 'all_clients':
                data['rows'] = len(_report.all_clients())

            if data:
                return {
                    'status': True,
                    'data': data
                }

    except Exception as e:
        logger.error(f':{update_fun.__name__}: {e}')

    return {
        'status': False
    }
