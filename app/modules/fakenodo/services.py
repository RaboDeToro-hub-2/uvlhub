from datetime import datetime
from app.modules.fakenodo.models import Fakenodo, FakenodoCreator, FakenodoFile, FakenodoMetadata
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
        fakenodo = Fakenodo()
        fakenodo.conceptrecid = self._hash_conceptrecid()
        metadata = self._create_metadata(data.get("metadata"))
        fakenodo.fakenodo_metadata = metadata
        return self.repository.save_deposition(fakenodo)

    def upload_file(self, deposition_id, data):
        fakenodo = self.get_deposition(deposition_id)
        file = FakenodoFile()
        file.name = data.get("name")
        fakenodo.files.append(file)
        return self.repository.save_deposition(fakenodo)

    def publish_deposition(self, deposition_id):
        fakenodo = self.get_deposition(deposition_id)
        fakenodo.fakenodo_metadata.publication_date = datetime.now()
        return self.repository.save_deposition(deposition_id)

    def delete_deposition(self, deposition_id):
        fakenodo = self.get_deposition(deposition_id)
        return self.repository.delete_deposition(fakenodo)

    def _create_metadata(self, data):
        metadata = FakenodoMetadata()
        metadata.title = data.get("title")
        metadata.publication_type = data.get("publication_type")
        metadata.description = data.get("description")
        metadata.access_right = data.get("access_right")
        metadata.license = data.get("license")

        creators = data.get("creators")
        if not creators:
            creators = []
        for creator_data in creators:
            creator = self.create_creator(creator_data)
            metadata.creators.append(creator)

        return metadata

    def _create_creator(self, data):
        fakenodo_creator = FakenodoCreator()
        fakenodo_creator.name = data.get("name")
        fakenodo_creator.affiliation = data.get("affiliation")
        fakenodo_creator.orcid = data.get("orcid")

        return fakenodo_creator

    def _hash_conceptrecid(self):
        return hash(datetime.now()) % 2_000_000_000
