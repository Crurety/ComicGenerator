from app import db
from datetime import datetime

class CharacterTemplate(db.Model):
    __tablename__ = 'character_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.JSON)
    reference_images = db.Column(db.JSON)  # Array of image URLs
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    comic_images = db.relationship('ComicImage', backref='character_template', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'features': self.features,
            'reference_images': self.reference_images,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }