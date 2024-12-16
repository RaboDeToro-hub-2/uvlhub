from app import db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relación con User
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)  # Relación con Community
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='notifications')
    community = db.relationship('Community', backref='notifications')

    def __repr__(self):
        return f'Notification<{self.id}>'
