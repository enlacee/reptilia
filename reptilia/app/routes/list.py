from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
from app.models.List import List
from app.models.Campaign import Campaign
from app.utils.handlers import exception_handler

@api.route('/campaigns', methods= ['POST'])
@jwt_required
@exception_handler
def campaigns():
    data = {
        'status': True
    }
    with Campaign() as campaign:
        data['campaigns'] = campaign.get_all()

    return jsonify(data)


@api.route('/update-campaign-status', methods= ['POST'])
@jwt_required
@exception_handler
def update_campaign_status():
    data = {
        'status': True
    }

    campaign_id = request.json.get('campaign_id')
    status = request.json.get('status')

    with Campaign() as _campaign:
        _campaign.update_status(campaign_id, status)

    return jsonify(data)

@api.route('/lists', methods= ['POST'])
@jwt_required
@exception_handler
def list_ids():
    data = {
        'status': True
    }

    with List() as _list:
        rows = _list.get_actives()

    if rows:
        data['lists'] = rows

    return jsonify(data)


@api.route('/all-lists', methods= ['POST'])
@jwt_required
@exception_handler
def all_lists():
    data = {
        'status': True
    }

    with List() as _list:
        rows = _list.get_all()

    if rows:
        data['lists'] = rows

    return jsonify(data)

@api.route('/create-list', methods= ['POST'])
@jwt_required
@exception_handler
def create_list():
    data = {
        'status': True
    }

    list_id = request.json.get('list_id')
    list_name = request.json.get('list_name')
    campaign_id = request.json.get('campaign_id')

    with List() as _list:
        _list.add(list_id, list_name, campaign_id)

    return jsonify(data)


@api.route('/update-list-status', methods= ['POST'])
@jwt_required
@exception_handler
def update_list_status():
    data = {
        'status': True
    }

    list_id = request.json.get('list_id')
    status = request.json.get('status')

    with List() as _list:
        _list.update_status(list_id, status)

    return jsonify(data)

