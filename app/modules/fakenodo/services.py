from app.modules.fakenodo.repositories import FakenodoRepository
from core.services.BaseService import BaseService


class FakenodoService(BaseService):
    def __init__(self):
        super().__init__(FakenodoRepository())

    def get_all_depositions(self):
        return self.repository.get_all_depositions()

    def get_deposition(self, deposition_id):
        return self.repository.get_deposition(deposition_id)

    def create_deposition(self, data):
        return self.repository.create_deposition(data)

    def upload_file(self, deposition_id, data):
        fakenodo = self.repository.get_deposition(deposition_id)
        return self.repository.add_file(fakenodo, data)

    def publish_deposition(self, deposition_id):
        fakenodo = self.repository.get_deposition(deposition_id)
        return self.repository.publish_deposition(fakenodo)
