from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models.project import Project
from app.models.comic import ComicImage
from app.models.user import User
from app import db

bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    
    # 使用聚合查询获取项目及其图片数量，解决 N+1 问题
    results = db.session.query(
        Project,
        func.count(ComicImage.id).label('image_count')
    ).outerjoin(
        ComicImage, Project.id == ComicImage.project_id
    ).filter(
        Project.owner_id == user_id
    ).group_by(Project.id).all()
    
    projects_data = []
    for project, image_count in results:
        # 使用更新后的 to_dict 方法传入预先计算的 count，避免 N+1
        # collaborators_count 暂时仍使用默认行为 (len)，如需优化可同样处理
        data = project.to_dict(comic_images_count=image_count)
        projects_data.append(data)
    
    return jsonify(projects_data)

@bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': '项目名称不能为空'}), 400
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=user_id
    )
    
    try:
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        print(f"Error creating project: {e}")
        db.session.rollback()
        return jsonify({'error': '创建项目失败'}), 500
    
    return jsonify(project.to_dict()), 201

@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问'}), 403
    
    return jsonify(project.to_dict())

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if project.owner_id != get_jwt_identity():
        return jsonify({'error': '只有项目所有者可以编辑项目'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '无效请求数据'}), 400
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新项目失败'}), 500
    
    return jsonify(project.to_dict())

@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if project.owner_id != get_jwt_identity():
        return jsonify({'error': '只有项目所有者可以删除项目'}), 403
    
    try:
        db.session.delete(project)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除项目失败'}), 500
    
    return jsonify({'message': '项目已删除'})