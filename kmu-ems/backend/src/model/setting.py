import bcrypt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from setting import db


class Setting:
    def __init__(self):
        self.id = None
        self.setting_key = None
        self.setting_value = None
        self.updated_at = None
    
    @staticmethod
    def hash_password(password):
        """密碼加密"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """密碼驗證"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @classmethod
    def get_setting(cls, setting_key):
        """獲取設定值"""
        try:
            result = db.session.execute(
                db.text("SELECT id, setting_key, setting_value FROM settings WHERE setting_key = :key"),
                {"key": setting_key}
            )
            row = result.fetchone()
            db.session.close()
            
            if not row:
                return None, f"Setting '{setting_key}' not found"
            
            setting = cls()
            setting.id = row[0]
            setting.setting_key = row[1]
            setting.setting_value = row[2]
            
            return setting, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"
    
    @classmethod
    def update_setting(cls, setting_key, setting_value):
        """更新設定值"""
        try:
            db.session.execute(
                db.text("""
                    INSERT INTO settings (setting_key, setting_value) 
                    VALUES (:key, :value) 
                    ON DUPLICATE KEY UPDATE 
                    setting_value = :value, updated_at = CURRENT_TIMESTAMP
                """),
                {"key": setting_key, "value": setting_value}
            )
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"
    
    @classmethod
    def verify_admin_password(cls, password):
        """驗證管理員密碼"""
        setting, error = cls.get_setting('admin_password')
        if error:
            return False, error
        
        if not setting:
            return False, "Admin password not configured"
        
        if not cls.verify_password(password, setting.setting_value):
            return False, "Invalid password"
        
        return True, None
    
    @classmethod
    def update_admin_password(cls, new_password):
        """更新管理員密碼"""
        hashed_password = cls.hash_password(new_password)
        success, error = cls.update_setting('admin_password', hashed_password)
        
        if not success:
            return False, error
        
        return True, None
    
    @classmethod
    def get_threshold_settings(cls):
        """獲取閾值設定"""
        try:
            result = db.session.execute(
                db.text("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'threshold_%'")
            )
            rows = result.fetchall()
            db.session.close()
            
            # 預設值
            default_settings = {
                "temp1": {"upperLimit": 28.0, "lowerLimit": 20.0},
                "hum1": {"upperLimit": 68.0},
                "temp2": {"upperLimit": 28.0, "lowerLimit": 20.0},
                "hum2": {"upperLimit": 68.0}
            }
            
            # 從資料庫覆蓋預設值
            for row in rows:
                setting_key = row[0]
                setting_value = float(row[1])
                
                if setting_key == 'threshold_temp1_upper':
                    default_settings['temp1']['upperLimit'] = setting_value
                elif setting_key == 'threshold_temp1_lower':
                    default_settings['temp1']['lowerLimit'] = setting_value
                elif setting_key == 'threshold_hum1_upper':
                    default_settings['hum1']['upperLimit'] = setting_value
                elif setting_key == 'threshold_temp2_upper':
                    default_settings['temp2']['upperLimit'] = setting_value
                elif setting_key == 'threshold_temp2_lower':
                    default_settings['temp2']['lowerLimit'] = setting_value
                elif setting_key == 'threshold_hum2_upper':
                    default_settings['hum2']['upperLimit'] = setting_value
            
            return default_settings, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"
    
    @classmethod
    def update_threshold_settings(cls, settings_data):
        """更新閾值設定"""
        try:
            # 更新temp1設定
            if 'temp1' in settings_data:
                temp1 = settings_data['temp1']
                if 'upperLimit' in temp1:
                    cls.update_setting('threshold_temp1_upper', str(temp1['upperLimit']))
                if 'lowerLimit' in temp1:
                    cls.update_setting('threshold_temp1_lower', str(temp1['lowerLimit']))
            
            # 更新hum1設定
            if 'hum1' in settings_data:
                hum1 = settings_data['hum1']
                if 'upperLimit' in hum1:
                    cls.update_setting('threshold_hum1_upper', str(hum1['upperLimit']))
            
            # 更新temp2設定
            if 'temp2' in settings_data:
                temp2 = settings_data['temp2']
                if 'upperLimit' in temp2:
                    cls.update_setting('threshold_temp2_upper', str(temp2['upperLimit']))
                if 'lowerLimit' in temp2:
                    cls.update_setting('threshold_temp2_lower', str(temp2['lowerLimit']))
            
            # 更新hum2設定
            if 'hum2' in settings_data:
                hum2 = settings_data['hum2']
                if 'upperLimit' in hum2:
                    cls.update_setting('threshold_hum2_upper', str(hum2['upperLimit']))
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"