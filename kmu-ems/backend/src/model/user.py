import jwt
import bcrypt
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from setting import db, Config


class User:
    def __init__(self):
        self.id = None
        self.username = None
        self.password = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }
    
    @staticmethod
    def hash_password(password):
        """密碼加密"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """密碼驗證"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token(username):
        """生成JWT token"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token_header):
        """驗證JWT token"""
        if not token_header or not token_header.startswith('Bearer '):
            return None
        
        token = token_header.split(' ')[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return payload['username']
        except:
            return None
    
    @classmethod
    def authenticate(cls, username, password):
        """用戶認證"""
        try:
            result = db.session.execute(
                db.text("SELECT id, username, password FROM users WHERE username = :username"),
                {"username": username}
            )
            row = result.fetchone()
            db.session.close()
            
            if not row or not cls.verify_password(password, row[2]):
                return None, "Invalid credentials"
            
            user = cls()
            # 使用mysql connector cursor.fetchone()返回tuple，不是物件
            # row[0]=id, row[1]=username, row[2]=password (對應SQL查詢順序)
            user.id = row[0]
            user.username = row[1]
            user.password = row[2]
            
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"