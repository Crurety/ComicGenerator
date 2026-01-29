#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.character import CharacterTemplate
from app.models.comic import ComicImage

def create_tables():
    """创建数据库表"""
    app = create_app('development')
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成!")

def drop_tables():
    """删除数据库表"""
    app = create_app('development')
    with app.app_context():
        print("正在删除数据库表...")
        db.drop_all()
        print("数据库表删除完成!")

def reset_database():
    """重置数据库"""
    app = create_app('development')
    with app.app_context():
        print("正在重置数据库...")
        db.drop_all()
        db.create_all()
        print("数据库重置完成!")

def create_sample_data():
    """创建示例数据"""
    app = create_app('development')
    with app.app_context():
        print("正在创建示例数据...")
        
        # 创建示例用户
        user = User(
            username='demo',
            email='demo@example.com'
        )
        user.set_password('demo123456')
        db.session.add(user)
        db.session.commit()
        
        # 创建示例项目
        project = Project(
            name='示例漫画项目',
            description='这是一个示例漫画项目',
            owner_id=user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 创建示例角色模板
        character = CharacterTemplate(
            name='示例角色',
            description='一个可爱的动漫角色',
            features={
                'hair': '黑色长发',
                'eyes': '蓝色大眼睛',
                'style': '动漫风格'
            },
            reference_images=[],
            owner_id=user.id
        )
        db.session.add(character)
        db.session.commit()
        
        # 创建示例漫画图片
        comic_image = ComicImage(
            project_id=project.id,
            character_template_id=character.id,
            prompt='可爱的动漫女孩在花园里散步',
            position_x=100,
            position_y=100,
            width=300,
            height=300,
            layer_order=0
        )
        db.session.add(comic_image)
        db.session.commit()
        
        print("示例数据创建完成!")
        print(f"用户: demo@example.com / demo123456")

def run_migrations():
    """运行数据库迁移"""
    print("正在运行数据库迁移...")
    try:
        subprocess.run(['flask', 'db', 'upgrade'], check=True)
        print("数据库迁移完成!")
    except subprocess.CalledProcessError as e:
        print(f"迁移失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python manage.py [create|drop|reset|sample|migrate]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        create_tables()
    elif command == 'drop':
        drop_tables()
    elif command == 'reset':
        reset_database()
    elif command == 'sample':
        create_sample_data()
    elif command == 'migrate':
        run_migrations()
    else:
        print("未知命令。可用命令: create, drop, reset, sample, migrate")
        sys.exit(1)