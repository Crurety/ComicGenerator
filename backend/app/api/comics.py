from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.comic import ComicImage
from app.models.project import Project
from app.models.character import CharacterTemplate
from app.services.midjourney import MidjourneyService
from app import db

bp = Blueprint('comics', __name__, url_prefix='/api/comics')

@bp.route('', methods=['POST'])
@jwt_required()
def create_comic_image():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ('project_id', 'prompt')):
        return jsonify({'error': '缺少必要字段'}), 400
    
    project = Project.query.get(data['project_id'])
    if not project or not project.has_access(user_id):
        return jsonify({'error': '无权限访问项目'}), 403
    
    comic_image = ComicImage(
        project_id=data['project_id'],
        prompt=data['prompt'],
        character_template_id=data.get('character_template_id'),
        image_url=data.get('image_url'),
        midjourney_task_id=data.get('midjourney_task_id'),
        position_x=data.get('position_x', 0),
        position_y=data.get('position_y', 0),
        width=data.get('width', 200),
        height=data.get('height', 200),
        layer_order=data.get('layer_order', 0)
    )
    
    try:
        db.session.add(comic_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建漫画图片失败'}), 500
    
    return jsonify(comic_image.to_dict()), 201

@bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_comic_image(image_id):
    comic_image = ComicImage.query.get_or_404(image_id)
    
    if not comic_image.project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问'}), 403
    
    return jsonify(comic_image.to_dict())

@bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_comics(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问项目'}), 403
    
    comic_images = ComicImage.query.filter_by(project_id=project_id).order_by(ComicImage.layer_order).all()
    return jsonify([c.to_dict() for c in comic_images])

@bp.route('/<int:image_id>', methods=['PUT'])
@jwt_required()
def update_comic_image(image_id):
    comic_image = ComicImage.query.get_or_404(image_id)
    
    if not comic_image.project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '无效请求数据'}), 400
    
    if 'prompt' in data:
        comic_image.prompt = data['prompt']
    if 'image_url' in data:
        comic_image.image_url = data['image_url']
    if 'status' in data:
        comic_image.status = data['status']
    if 'position_x' in data:
        comic_image.position_x = data['position_x']
    if 'position_y' in data:
        comic_image.position_y = data['position_y']
    if 'width' in data:
        comic_image.width = data['width']
    if 'height' in data:
        comic_image.height = data['height']
    if 'layer_order' in data:
        comic_image.layer_order = data['layer_order']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新漫画图片失败'}), 500
    
    return jsonify(comic_image.to_dict())

@bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_comic_image(image_id):
    comic_image = ComicImage.query.get_or_404(image_id)
    
    if not comic_image.project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问'}), 403
    
    try:
        db.session.delete(comic_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除漫画图片失败'}), 500
    
    return jsonify({'message': '漫画图片已删除'})

@bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_comic_images():
    data = request.get_json()
    
    if not data or 'project_id' not in data or 'image_orders' not in data:
        return jsonify({'error': '缺少必要字段'}), 400
    
    project = Project.query.get(data['project_id'])
    if not project or not project.has_access(get_jwt_identity()):
        return jsonify({'error': '无权限访问项目'}), 403
    
    try:
        for order_data in data['image_orders']:
            comic_image = ComicImage.query.get(order_data['image_id'])
            if comic_image and comic_image.project_id == data['project_id']:
                comic_image.layer_order = order_data['order']
        
        db.session.commit()
        return jsonify({'message': '图层顺序已更新'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新图层顺序失败'}), 500

@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_comic_image():
    data = request.get_json()
    
    if not data or not data.get('prompt'):
        return jsonify({'error': 'Prompt is required'}), 400
        
    mj_service = MidjourneyService()
    try:
        character_template = None
        if data.get('character_template_id'):
            character_template = CharacterTemplate.query.get(data['character_template_id'])
            
        result = mj_service.generate_image(data['prompt'], character_template)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/status/<task_id>', methods=['GET'])
@jwt_required()
def check_generation_status(task_id):
    mj_service = MidjourneyService()
    try:
        result = mj_service.check_task_status(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500