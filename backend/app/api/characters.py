from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.character import CharacterTemplate
from app import db

bp = Blueprint('characters', __name__, url_prefix='/api/characters')

@bp.route('', methods=['GET'])
@jwt_required()
def get_characters():
    user_id = get_jwt_identity()
    characters = CharacterTemplate.query.filter_by(owner_id=user_id).all()
    return jsonify([c.to_dict() for c in characters])

@bp.route('', methods=['POST'])
@jwt_required()
def create_character():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': '角色名称不能为空'}), 400
    
    character = CharacterTemplate(
        name=data['name'],
        description=data.get('description', ''),
        features=data.get('features', {}),
        reference_images=data.get('reference_images', []),
        owner_id=user_id
    )
    
    try:
        db.session.add(character)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建角色模板失败'}), 500
    
    return jsonify(character.to_dict()), 201

@bp.route('/<int:character_id>', methods=['GET'])
@jwt_required()
def get_character(character_id):
    character = CharacterTemplate.query.get_or_404(character_id)
    
    if character.owner_id != get_jwt_identity():
        return jsonify({'error': '无权限访问'}), 403
    
    return jsonify(character.to_dict())

@bp.route('/<int:character_id>', methods=['PUT'])
@jwt_required()
def update_character(character_id):
    character = CharacterTemplate.query.get_or_404(character_id)
    
    if character.owner_id != get_jwt_identity():
        return jsonify({'error': '只有所有者可以编辑角色模板'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '无效请求数据'}), 400
    
    if 'name' in data:
        character.name = data['name']
    if 'description' in data:
        character.description = data['description']
    if 'features' in data:
        character.features = data['features']
    if 'reference_images' in data:
        character.reference_images = data['reference_images']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新角色模板失败'}), 500
    
    return jsonify(character.to_dict())

@bp.route('/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_character(character_id):
    character = CharacterTemplate.query.get_or_404(character_id)
    
    if character.owner_id != get_jwt_identity():
        return jsonify({'error': '只有所有者可以删除角色模板'}), 403
    
    try:
        db.session.delete(character)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除角色模板失败'}), 500
    
    return jsonify({'message': '角色模板已删除'})