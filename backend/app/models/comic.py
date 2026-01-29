from app import db
from datetime import datetime

class ComicImage(db.Model):
    __tablename__ = 'comic_images'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    character_template_id = db.Column(db.Integer, db.ForeignKey('character_templates.id'))
    prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    midjourney_task_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=200)
    height = db.Column(db.Integer, default=200)
    layer_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'character_template_id': self.character_template_id,
            'prompt': self.prompt,
            'image_url': self.image_url,
            'midjourney_task_id': self.midjourney_task_id,
            'status': self.status,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'width': self.width,
            'height': self.height,
            'layer_order': self.layer_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }