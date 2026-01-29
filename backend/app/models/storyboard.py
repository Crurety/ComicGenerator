from app import db
from datetime import datetime

class Storyboard(db.Model):
    __tablename__ = 'storyboards'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    
    # 分镜内容
    description = db.Column(db.Text, nullable=False)  # 画面描述
    camera = db.Column(db.String(100))  # 镜头语言
    dialogue = db.Column(db.Text)  # 对话/旁白
    mood = db.Column(db.String(100))  # 情感/氛围
    
    # 关联生成的图片
    comic_image_id = db.Column(db.Integer, db.ForeignKey('comic_images.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    comic_image = db.relationship('ComicImage', backref='storyboard', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'sequence': self.sequence,
            'description': self.description,
            'camera': self.camera,
            'dialogue': self.dialogue,
            'mood': self.mood,
            'comic_image_id': self.comic_image_id,
            'image_url': self.comic_image.image_url if self.comic_image else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
