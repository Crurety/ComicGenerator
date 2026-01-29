import re
from datetime import datetime

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "密码必须包含大小写字母和数字"
    
    return True, "密码强度合格"

def generate_filename(original_filename):
    """生成安全的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
    return f"{timestamp}_{name}.{ext}"

def sanitize_prompt(prompt):
    """清理用户输入的prompt"""
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        prompt = prompt.replace(char, '')
    
    # 限制长度
    if len(prompt) > 1000:
        prompt = prompt[:1000]
    
    return prompt.strip()