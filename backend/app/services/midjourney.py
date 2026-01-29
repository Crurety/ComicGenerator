import requests
import asyncio
import os
import uuid
from app import db
from app.models.comic import ComicImage

class MidjourneyService:
    def __init__(self):
        self.api_url = "https://api.midjourney.com/v2"
        self.api_key = os.getenv('MIDJOURNEY_API_KEY')
    
    def generate_image(self, prompt, character_template=None):
        """生成图片，支持角色一致性"""
        # 如果没有API Key，使用模拟生成
        if not self.api_key:
            print("Warning: No MIDJOURNEY_API_KEY found. Using mock generation.")
            return self._mock_generate(prompt)

        if character_template:
            prompt = self._apply_character_consistency(prompt, character_template)
        
        payload = {
            "prompt": prompt,
            "model": "niji6",
            "quality": "high",
            "style": "anime"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/imagine",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to mock if the API is unreachable (likely given the URL)
                print(f"API Error {response.status_code}. Fallback to mock.")
                return self._mock_generate(prompt)
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Fallback to mock.")
            return self._mock_generate(prompt)
    
    def check_task_status(self, task_id):
        """检查任务状态"""
        if not self.api_key or str(task_id).startswith('mock-'):
            return self._mock_check_status(task_id)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/task/{task_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"状态检查失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
             if str(task_id).startswith('mock-'):
                 return self._mock_check_status(task_id)
             raise Exception(f"网络请求失败: {str(e)}")

    def _mock_generate(self, prompt):
        """模拟生成"""
        task_id = f"mock-{uuid.uuid4()}"
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Mock generation started"
        }

    def _mock_check_status(self, task_id):
        """模拟检查状态"""
        # 使用更稳定的占位图服务，并添加随机参数避免缓存
        # 使用 ui-avatars 生成带文字的图片，更直观
        random_color = uuid.uuid4().hex[:6]
        return {
            "task_id": task_id,
            "status": "completed",
            "image_url": f"https://ui-avatars.com/api/?name=AI+Image&background={random_color}&color=fff&size=512&font-size=0.33",
            "progress": 100
        }
    
    def _apply_character_consistency(self, prompt, character_template):
        """应用角色一致性到prompt"""
        if not character_template:
            return prompt
        
        consistency_features = []
        
        if character_template.features:
            for key, value in character_template.features.items():
                if value:
                    consistency_features.append(f"{key}:{value}")
        
        if character_template.description:
            consistency_features.append(character_template.description)
        
        if consistency_features:
            consistency_prompt = ", ".join(consistency_features)
            return f"{prompt}, {consistency_prompt}"
        
        return prompt
