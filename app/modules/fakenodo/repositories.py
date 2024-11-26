from app.modules.fakenodo.models import Fakenodo
from core.repositories.BaseRepository import BaseRepository


class FakenodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Fakenodo)

    def get_all_depositions(self):
        return self.model.query.all()

    def get_deposition(self, deposition_id):
        return self.model.query.get(deposition_id)

    def save_deposition(self, fakenodo):
        self.session.add(fakenodo)
        self.session.commit()
        return fakenodo

    def delete_deposition(self, fakenodo):
        self.session.delete(fakenodo)
        self.session.commit()
