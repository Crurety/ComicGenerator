from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.project import Project
from app.models.storyboard import Storyboard
from app.models.comic import ComicImage
from app.services.gemini import get_gemini_service
from app import db
import uuid

bp = Blueprint('stories', __name__, url_prefix='/api/stories')

@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_story():
    """Step 1: 内容理解与分镜生成 - 使用 Gemini AI"""
    data = request.get_json()
    story_text = data.get('story_text')
    
    if not story_text:
        return jsonify({'error': '请提供故事内容'}), 400

    # 使用 Gemini 服务进行故事分析
    gemini_service = get_gemini_service()
    scenes = gemini_service.analyze_story(story_text)
        
    return jsonify({'scenes': scenes})

@bp.route('/save', methods=['POST'])
@jwt_required()
def save_storyboards():
    """保存分镜脚本"""
    user_id = get_jwt_identity()
    data = request.get_json()
    project_id = data.get('project_id')
    scenes = data.get('scenes', [])
    
    project = Project.query.get(project_id)
    if not project or not project.has_access(user_id):
        return jsonify({'error': '无权限访问项目'}), 403
        
    try:
        saved_storyboards = []
        # 先清除旧的分镜 (简单处理)
        Storyboard.query.filter_by(project_id=project_id).delete()
        
        for scene in scenes:
            storyboard = Storyboard(
                project_id=project_id,
                sequence=scene['sequence'],
                description=scene['description'],
                camera=scene.get('camera'),
                dialogue=scene.get('dialogue'),
                mood=scene.get('mood')
            )
            db.session.add(storyboard)
            saved_storyboards.append(storyboard)
            
        db.session.commit()
        return jsonify([s.to_dict() for s in saved_storyboards])
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/generate_all', methods=['POST'])
@jwt_required()
def generate_all_images():
    """Step 3: 批量生成漫画图片 - 使用 Gemini AI"""
    user_id = get_jwt_identity()
    data = request.get_json()
    project_id = data.get('project_id')
    
    project = Project.query.get(project_id)
    if not project or not project.has_access(user_id):
        return jsonify({'error': '无权限访问项目'}), 403
        
    storyboards = Storyboard.query.filter_by(project_id=project_id).order_by(Storyboard.sequence).all()
    
    if not storyboards:
        return jsonify({'error': '没有找到分镜脚本'}), 404
    
    # 使用 Gemini 服务生成图片
    gemini_service = get_gemini_service()
    results = []
    
    try:
        for sb in storyboards:
            # 构建 Prompt (移除 Midjourney 特有的参数如 --ar 16:9)
            full_prompt = f"{sb.description}, {sb.camera}, {sb.mood}"
            
            # 使用 Gemini 生成图片
            # Gemini 的图片生成是同步的，直接返回结果
            result = gemini_service.generate_image(full_prompt)
            
            image_url = result.get('image_url')

            if image_url:
                # 创建 ComicImage 记录
                comic_image = ComicImage(
                    project_id=project_id,
                    prompt=full_prompt,
                    image_url=image_url,
                    midjourney_task_id=result.get('task_id'),  # 保留字段名以兼容
                    position_x=0,
                    position_y=0,
                    width=400,
                    height=225, # 16:9 比例
                    layer_order=sb.sequence
                )
                db.session.add(comic_image)
                db.session.flush() # 获取 ID
                
                # 关联到分镜
                sb.comic_image_id = comic_image.id
                results.append(comic_image.to_dict())
        
        db.session.commit()
        return jsonify({'message': '批量生成完成', 'images': results})
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/list/<int:project_id>', methods=['GET'])
@jwt_required()
def get_storyboards(project_id):
    storyboards = Storyboard.query.filter_by(project_id=project_id).order_by(Storyboard.sequence).all()
    return jsonify([s.to_dict() for s in storyboards])
