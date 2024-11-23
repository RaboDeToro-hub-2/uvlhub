from flask import request
from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService

fakenodo_service = FakenodoService()


@fakenodo_bp.route('/fakenodo', methods=['GET'])
def index():
    data = fakenodo_service.get_all_depositions()
    return [d.to_dict() for d in data], 200


@fakenodo_bp.route('/fakenodo/<deposition_id>', methods=['GET'])
def get_deposition(deposition_id):
    return fakenodo_service.get_deposition(deposition_id).to_dict()


@fakenodo_bp.route('/fakenodo', methods=['POST'])
def create_deposition():
    data = request.get_json()
    return fakenodo_service.create_deposition(data).to_dict(), 201


@fakenodo_bp.route('/fakenodo/<deposition_id>/files', methods=['POST'])
def upload_file(deposition_id):
    data = request.form
    return fakenodo_service.upload_file(deposition_id, data).to_dict(), 201


@fakenodo_bp.route('/fakenodo/<deposition_id>/actions/publish', methods=['POST'])
def publish_deposition(deposition_id):
    return fakenodo_service.publish_deposition(deposition_id).to_dict()
