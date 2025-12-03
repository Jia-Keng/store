from flask import request
from flask_restx import abort
from ..model.user import User


class AuthController:
    """處理登入認證"""
    
    @staticmethod
    def login():
        """用戶登入"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            abort(400, 'Username and password are required')

        user, error = User.authenticate(username, password)
        if error:
            if "Database" in error:
                abort(500, error)
            else:
                abort(401, error)

        token = User.generate_token(username)
        
        return {
            'token': token,
            'username': username,
            'expires_in': 86400 # 24小時
        }
    
    @staticmethod
    def setting_login():
        """設定登入，只需要密碼"""
        data = request.get_json()
        password = data.get('password')

        if not password:
            abort(400, 'Password is required')

        # 目前固定密碼為 "admin0000"
        if password != "admin0000":
            abort(401, 'Invalid password')

        # 生成token給設定頁面使用
        token = User.generate_token('setting')
        
        return {
            'token': token,
            'expires_in': 86400 # 24小時
        }
    
    @staticmethod
    def require_auth():
        """從http header提取並且做驗證 JWT、解析token 獲取用戶身份、無效token做拒絕"""
        username = User.verify_token(request.headers.get('Authorization'))
        if not username:
            abort(401, 'Invalid or missing token')
        return username