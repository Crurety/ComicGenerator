from app import db
from datetime import datetime

project_collaborators = db.Table('project_collaborators',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), nullable=False),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('role', db.String(20), default='viewer'),
    db.Column('invited_at', db.DateTime, server_default=db.func.now())
)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    comic_images = db.relationship('ComicImage', backref='project', lazy=True, cascade='all, delete-orphan')
    collaborators = db.relationship('User', secondary=project_collaborators, backref='collaborating_projects')
    
    def has_access(self, user_id):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            pass
            
        if self.owner_id == user_id:
            return True
        return any(collab.id == user_id for collab in self.collaborators)
    
    def to_dict(self, comic_images_count=None, collaborators_count=None):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if comic_images_count is not None:
            data['comic_images_count'] = comic_images_count
        else:
            data['comic_images_count'] = len(self.comic_images)
            
        if collaborators_count is not None:
            data['collaborators_count'] = collaborators_count
        else:
            data['collaborators_count'] = len(self.collaborators)
            
        return data