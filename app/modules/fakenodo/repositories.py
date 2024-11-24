from datetime import datetime
from app.modules.fakenodo.models import Fakenodo, FakenodoFile, FakenodoMetadata, FakenodoCreator
from core.repositories.BaseRepository import BaseRepository


class FakenodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Fakenodo)

    def get_all_depositions(self):
        return self.model.query.all()

    def get_deposition(self, deposition_id):
        return self.model.query.get(deposition_id)

    def create_deposition(self, data):
        fakenodo = Fakenodo()
        fakenodo.conceptrecid = self._hash_conceptrecid()
        metadata = self.create_metadata(data.get("metadata"))
        fakenodo.fakenodo_metadata = metadata
        self.session.add(fakenodo)
        self.session.commit()
        return fakenodo

    def add_file(self, fakenodo, data):
        file = FakenodoFile()
        file.name = data.get("name")
        fakenodo.files.append(file)
        self.session.commit()
        return fakenodo

    def publish_deposition(self, fakenodo):
        fakenodo.fakenodo_metadata.publication_date = datetime.now()
        self.session.commit()
        return fakenodo

    def create_metadata(self, data):
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

    def create_creator(self, data):
        fakenodo_creator = FakenodoCreator()
        fakenodo_creator.name = data.get("name")
        fakenodo_creator.affiliation = data.get("affiliation")
        fakenodo_creator.orcid = data.get("orcid")

        return fakenodo_creator

    def _hash_conceptrecid(self):
        return hash(datetime.now()) % 2_000_000_000
