from flask import request
from flask_restx import abort
from ..model.user import User
from ..model.setting import Setting


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

        # 從資料庫驗證設定密碼
        is_valid, error = Setting.verify_admin_password(password)
        if not is_valid:
            if "Database" in error:
                abort(500, error)
            else:
                abort(401, error)

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
    
    @staticmethod
    def update_user_password():
        """更新用戶密碼"""
        username = AuthController.require_auth()
        data = request.get_json()
        
        original_password = data.get('originalPassword')
        new_password = data.get('newPassword')
        
        if not original_password or not new_password:
            abort(400, 'originalPassword and newPassword are required')
        
        # 驗證當前密碼
        user, error = User.authenticate(username, original_password)
        if error:
            if "Database" in error:
                abort(500, error)
            else:
                abort(401, 'Invalid original password')
        
        # 更新密碼
        try:
            hashed_password = User.hash_password(new_password)
            from setting import db
            db.session.execute(
                db.text("UPDATE users SET password = :password WHERE username = :username"),
                {"password": hashed_password, "username": username}
            )
            db.session.commit()
            
            return {'message': 'Password updated successfully'}
        except Exception as e:
            db.session.rollback()
            abort(500, f"Database error: {str(e)}")
    
    @staticmethod
    def update_setting_password():
        """更新設定密碼"""
        username = AuthController.require_auth()
        
        # 檢查是否為設定用戶
        if username != 'setting':
            abort(403, 'Access denied: not a setting user')
        
        data = request.get_json()
        original_password = data.get('originalPassword')
        new_password = data.get('newPassword')
        
        if not original_password or not new_password:
            abort(400, 'originalPassword and newPassword are required')
        
        # 驗證當前設定密碼
        is_valid, error = Setting.verify_admin_password(original_password)
        if not is_valid:
            if "Database" in error:
                abort(500, error)
            else:
                abort(401, 'Invalid original password')
        
        # 更新設定密碼
        success, error = Setting.update_admin_password(new_password)
        if not success:
            abort(500, error)
        
        return {'message': 'Setting password updated successfully'}
    
    @staticmethod
    def get_threshold_settings():
        """獲取閾值設定"""
        settings, error = Setting.get_threshold_settings()
        if error:
            abort(500, error)
        
        return settings
    
    @staticmethod
    def update_threshold_settings():
        """更新閾值設定"""
        username = AuthController.require_auth()
        
        # 檢查是否為設定用戶
        if username != 'setting':
            abort(403, 'Access denied: not a setting user')
        
        data = request.get_json()
        
        if not data:
            abort(400, 'Settings data is required')
        
        # 更新設定
        success, error = Setting.update_threshold_settings(data)
        if not success:
            abort(500, error)
        
        return {'message': 'Settings updated successfully'}