"""
Gemini AI 服务模块
使用新版 google-genai SDK
支持 gemini-3-flash-preview 模型 (文本) 和 gemini-2.5-flash-image (图像生成)
通过环境变量配置代理
"""
import os
import json
import re
import base64
import uuid
from pathlib import Path

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        self.model_name = "gemini-3-flash-preview"
        self.image_model_name = "gemini-2.5-flash-image"
        
        # 设置图片保存目录
        self.image_save_dir = Path(os.getenv('IMAGE_SAVE_DIR', 'static/images'))
        self.image_save_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置代理环境变量 (httpx 会自动读取)
        http_proxy = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
        if http_proxy:
            os.environ['HTTP_PROXY'] = http_proxy
            os.environ['HTTPS_PROXY'] = http_proxy
            os.environ['ALL_PROXY'] = http_proxy
            print(f"Gemini: Using proxy {http_proxy}")
        
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                print(f"Gemini: Initialized with model {self.model_name}")
            except Exception as e:
                print(f"Gemini: Failed to initialize client: {e}")
                self.client = None
        else:
            print("Warning: No GEMINI_API_KEY found. Story analysis will use mock data.")
    
    def analyze_story(self, story_text):
        """
        分析故事文本，生成分镜脚本
        
        Args:
            story_text: 用户输入的故事描述
            
        Returns:
            list: 分镜场景列表
        """
        if not self.client:
            return self._mock_analyze(story_text)
        
        prompt = f"""你是一位专业的漫画分镜师。请分析以下故事内容，将其拆分成适合漫画表现的分镜脚本。

故事内容：
{story_text}

请按照以下JSON格式返回分镜脚本（直接返回JSON数组，不要包含其他文字）：
[
  {{
    "sequence": 1,
    "description": "详细描述这个画面的场景、人物动作、表情等，用于AI绘图",
    "camera": "镜头类型，如：全景(Wide Shot)、中景(Medium Shot)、特写(Close Up)、仰拍(Low Angle)、俯拍(High Angle)",
    "dialogue": "该画面中的对话或旁白，如果没有则写'无'",
    "mood": "画面的情绪氛围，如：紧张、欢快、悲伤、神秘等"
  }}
]

要求：
1. 根据故事内容合理拆分，通常3-8个分镜为宜
2. 每个分镜的description要详细具体，便于AI绘图理解
3. 镜头类型要多样化，增加视觉变化
4. 保持故事的连贯性和节奏感

只返回JSON数组，不要有其他任何文字说明。"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result_text = response.text.strip()
            
            # 尝试提取JSON
            scenes = self._parse_json_response(result_text)
            
            if scenes:
                return scenes
            else:
                print("Failed to parse Gemini response, falling back to mock")
                return self._mock_analyze(story_text)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._mock_analyze(story_text)
    
    def _parse_json_response(self, text):
        """解析Gemini返回的JSON"""
        try:
            # 直接尝试解析
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON数组
        try:
            # 查找 [ ] 包裹的内容
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        
        # 尝试移除可能的markdown代码块标记
        try:
            clean_text = re.sub(r'^```json\s*', '', text)
            clean_text = re.sub(r'^```\s*', '', clean_text)
            clean_text = re.sub(r'\s*```$', '', clean_text)
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def generate_image(self, prompt, character_template=None):
        """
        使用 Gemini 生成图像
        
        Args:
            prompt: 图像描述提示词
            character_template: 可选的角色模板，用于保持角色一致性
            
        Returns:
            dict: 包含 image_url 和 task_id 的结果
        """
        if not self.client:
            print("Warning: No Gemini client. Using mock image generation.")
            return self._mock_generate_image(prompt)
        
        # 应用角色一致性
        if character_template:
            prompt = self._apply_character_consistency(prompt, character_template)
        
        # 增强 prompt 以适应漫画风格
        enhanced_prompt = f"{prompt}, anime style, manga art, high quality illustration, detailed artwork"
        
        try:
            from google.genai import types
            
            # 关键：必须设置 response_modalities 为 ['Image'] 才能生成图片
            # 同时设置 image_config 来控制图片宽高比
            response = self.client.models.generate_content(
                model=self.image_model_name,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],
                    image_config=types.ImageConfig(
                        aspect_ratio="16:9",  # 漫画常用宽高比
                    )
                )
            )
            
            # 处理响应，提取图像
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data is not None:
                            # 提取图像数据
                            image_data = part.inline_data.data
                            mime_type = getattr(part.inline_data, 'mime_type', None) or 'image/png'
                            
                            # 生成唯一文件名
                            task_id = f"gemini-{uuid.uuid4()}"
                            extension = 'png' if 'png' in mime_type else 'jpg'
                            filename = f"{task_id}.{extension}"
                            filepath = self.image_save_dir / filename
                            
                            # 保存图像文件
                            with open(filepath, 'wb') as f:
                                if isinstance(image_data, str):
                                    # Base64 编码的数据
                                    f.write(base64.b64decode(image_data))
                                else:
                                    # 二进制数据
                                    f.write(image_data)
                            
                            print(f"Gemini: Image saved to {filepath}")
                            
                            # 返回相对 URL 路径
                            image_url = f"/static/images/{filename}"
                            
                            return {
                                "task_id": task_id,
                                "status": "completed",
                                "image_url": image_url,
                                "progress": 100
                            }
            
            # 如果没有找到图像数据
            print(f"No image data in Gemini response. Response: {response}")
            return self._mock_generate_image(prompt)
            
        except Exception as e:
            import traceback
            print(f"Gemini image generation error: {e}")
            traceback.print_exc()
            return self._mock_generate_image(prompt)
    
    def _mock_generate_image(self, prompt):
        """模拟图像生成（当API不可用时）"""
        task_id = f"mock-{uuid.uuid4()}"
        # 使用 ui-avatars 生成带文字的占位图
        random_color = uuid.uuid4().hex[:6]
        return {
            "task_id": task_id,
            "status": "completed",
            "image_url": f"https://ui-avatars.com/api/?name=AI+Image&background={random_color}&color=fff&size=512&font-size=0.33",
            "progress": 100
        }
    
    def check_task_status(self, task_id):
        """
        检查任务状态
        对于 Gemini 来说，图像生成是同步的，所以这个方法主要用于兼容性
        """
        if str(task_id).startswith('mock-'):
            random_color = uuid.uuid4().hex[:6]
            return {
                "task_id": task_id,
                "status": "completed",
                "image_url": f"https://ui-avatars.com/api/?name=AI+Image&background={random_color}&color=fff&size=512&font-size=0.33",
                "progress": 100
            }
        
        # 对于真实的 Gemini 生成，图像已经同步返回
        # 这里返回已完成状态
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100
        }
    
    def _apply_character_consistency(self, prompt, character_template):
        """应用角色一致性到prompt"""
        if not character_template:
            return prompt
        
        consistency_features = []
        
        if hasattr(character_template, 'features') and character_template.features:
            for key, value in character_template.features.items():
                if value:
                    consistency_features.append(f"{key}:{value}")
        
        if hasattr(character_template, 'description') and character_template.description:
            consistency_features.append(character_template.description)
        
        if consistency_features:
            consistency_prompt = ", ".join(consistency_features)
            return f"{prompt}, {consistency_prompt}"
        
        return prompt
    
    def _mock_analyze(self, story_text):
        """
        智能模拟分析（当API不可用时）
        根据用户输入的故事内容生成相关的分镜脚本
        """
        # 尝试按句子分割故事
        sentences = re.split(r'[。！？\n]+', story_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
        
        if not sentences:
            sentences = [story_text[:100] if len(story_text) > 100 else story_text]
        
        # 限制分镜数量
        num_scenes = min(max(len(sentences), 2), 8)
        
        # 镜头类型循环
        camera_types = [
            "全景 (Wide Shot)",
            "中景 (Medium Shot)", 
            "特写 (Close Up)",
            "仰拍 (Low Angle)",
            "俯拍 (High Angle)",
            "远景 (Long Shot)",
            "过肩镜头 (Over the Shoulder)",
            "主观镜头 (POV Shot)"
        ]
        
        # 情绪关键词映射
        mood_keywords = {
            '开心': '欢快', '快乐': '欢快', '笑': '欢快', '高兴': '欢快',
            '伤心': '悲伤', '哭': '悲伤', '难过': '悲伤', '痛苦': '悲伤',
            '害怕': '恐惧', '恐怖': '恐惧', '可怕': '恐惧',
            '紧张': '紧张', '危险': '紧张', '战斗': '紧张', '打': '紧张',
            '神秘': '神秘', '奇怪': '神秘', '秘密': '神秘',
            '爱': '浪漫', '喜欢': '浪漫', '心': '浪漫',
            '愤怒': '激烈', '怒': '激烈', '生气': '激烈'
        }
        
        default_moods = ['期待', '紧张', '震惊', '激烈', '英勇', '释然', '感动', '神秘']
        
        scenes = []
        for i in range(num_scenes):
            # 获取对应的故事片段
            if i < len(sentences):
                description = sentences[i]
            else:
                description = f"故事继续发展..."
            
            # 检测情绪
            detected_mood = default_moods[i % len(default_moods)]
            for keyword, mood in mood_keywords.items():
                if keyword in description:
                    detected_mood = mood
                    break
            
            # 生成对话
            if i == 0:
                dialogue = "旁白：故事开始了..."
            elif '说' in description or '道' in description or '"' in description or '"' in description:
                dialogue = "（角色对话）"
            else:
                dialogue = "无"
            
            scene = {
                "sequence": i + 1,
                "description": f"{description}，漫画风格，高质量，细节丰富",
                "camera": camera_types[i % len(camera_types)],
                "dialogue": dialogue,
                "mood": detected_mood
            }
            scenes.append(scene)
        
        return scenes


# 单例实例
_gemini_service = None

def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
