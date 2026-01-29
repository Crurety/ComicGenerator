"""
Gemini AI 服务模块
使用新版 google-genai SDK
支持 gemini-3-flash-preview 模型
通过环境变量配置代理
"""
import os
import json
import re

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        self.model_name = "gemini-3-flash-preview"
        
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
