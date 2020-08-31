from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.routes import api
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

@api.route('/create-campaign', methods= ['POST'])
@jwt_required
@exception_handler
def create_campaigns():
    data = {
        'status': True
    }
    campaign_name = request.json.get('campaign_name')
    campaign_id = request.json.get('campaign_id')

    with Campaign() as _campaign:
        _campaign.add(campaign_id, campaign_name)

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
