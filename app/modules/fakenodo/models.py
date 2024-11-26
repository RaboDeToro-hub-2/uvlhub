from app import db


class Fakenodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conceptrecid = db.Column(db.Integer, nullable=False)
    fakenodo_metadata = db.relationship('FakenodoMetadata', backref='fakenodo', uselist=False, lazy=False)
    files = db.relationship('FakenodoFile', backref='fakenodo', lazy=True)

    def __repr__(self):
        return f'Fakenodo<{self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "conceptrecid": self.conceptrecid,
            "metadata": self.fakenodo_metadata.to_dict(),
            "files": [file.to_dict() for file in self.files]
        }


association_table = db.Table(
    'fakenodo_metadata_creator',
    db.Column('fakenodo_metadata_id', db.Integer, db.ForeignKey('fakenodo_metadata.id')),
    db.Column('fakenodo_creator_id', db.Integer, db.ForeignKey('fakenodo_creator.id'))
)


class FakenodoMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    publication_type = db.Column(db.String(255), nullable=True)
    publication_date = db.Column(db.DateTime, nullable=True)
    access_right = db.Column(db.String(255), nullable=True)
    license = db.Column(db.String(255), nullable=True)
    creators = db.relationship('FakenodoCreator', secondary=association_table,
                               backref=db.backref('fakenodo_metadata', lazy=True), lazy=False)
    fakenodo_id = db.Column(db.Integer, db.ForeignKey('fakenodo.id'), nullable=False)

    def __repr__(self):
        return f'FakenodoMetadata<{self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "publication_type": self.publication_type,
            "publication_date": self.publication_date,
            "access_right": self.access_right,
            "license": self.license,
            "creators": [creator.to_dict() for creator in self.creators]
        }


class FakenodoCreator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    affiliation = db.Column(db.String(255), nullable=True)
    orcid = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'FakenodoCreator<{self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "affiliation": self.affiliation,
            "orcid": self.orcid
        }


class FakenodoFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    fakenodo_id = db.Column(db.Integer, db.ForeignKey('fakenodo.id'), nullable=False)

    def __repr__(self):
        return f'FakenodoFile<{self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
