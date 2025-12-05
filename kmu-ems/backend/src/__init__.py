from flask import Flask
from flask_cors import CORS
from setting import Config, db
import bcrypt


def init_default_users():
    """初始化用戶，當表為空會初始化"""
    try:
        # 檢查用戶表是否存在
        table_check = db.session.execute(db.text("SHOW TABLES LIKE 'users'"))
        if table_check.fetchone() is None:
            print("users table does not exist, skipping user initialization")
            return
            
        # 檢查是否有用戶
        result = db.session.execute(db.text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]

        if count == 0:
            # 生成加密密碼
            admin_hash = bcrypt.hashpw('admin0000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 插入預設用戶
            admin_sql = db.text('INSERT INTO users (username, password) VALUES (:username, :password)')
            db.session.execute(admin_sql, {'username': 'admin', 'password': admin_hash})

            db.session.commit()
            print("Default user created: admin")
        else:
            print(f"Users already has {count} users, skip init")

    except Exception as e:
        print(f"Error init users: {e}")
        db.session.rollback()


def init_settings_table():
    """初始化設定表格，確保表格存在"""
    try:
        # 檢查settings表是否存在
        table_check = db.session.execute(db.text("SHOW TABLES LIKE 'settings'"))
        if table_check.fetchone() is None:
            print("Creating settings table...")
            # 建立settings表
            db.session.execute(db.text("""
                CREATE TABLE `settings` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `setting_key` varchar(100) NOT NULL,
                  `setting_value` text,
                  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `setting_key` (`setting_key`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # 插入預設設定密碼
            admin_hash = bcrypt.hashpw('admin0000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.execute(
                db.text("INSERT INTO settings (setting_key, setting_value) VALUES (:key, :value)"),
                {"key": "admin_password", "value": admin_hash}
            )
            
            db.session.commit()
            print("Settings table created and default admin password set")
        else:
            # 檢查是否有admin_password設定
            result = db.session.execute(
                db.text("SELECT COUNT(*) FROM settings WHERE setting_key = 'admin_password'")
            )
            count = result.fetchone()[0]
            
            if count == 0:
                # 插入預設admin密碼
                admin_hash = bcrypt.hashpw('admin0000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.execute(
                    db.text("INSERT INTO settings (setting_key, setting_value) VALUES (:key, :value)"),
                    {"key": "admin_password", "value": admin_hash}
                )
                db.session.commit()
                print("Default admin password added to existing settings table")
            else:
                print("Settings table exists with admin password configured")

    except Exception as e:
        print(f"Error initializing settings table: {e}")
        db.session.rollback()

def init_test_data():
    """初始化測試資料，當表存在且為空時會初始化"""
    try:
        # 檢查表是否存在
        table_check = db.session.execute(db.text("SHOW TABLES LIKE 'kmu_ems_data'"))
        if table_check.fetchone() is None:
            print("kmu_ems_data table does not exist, skipping test data initialization")
            return

        # 檢查是否已有測試資料
        result = db.session.execute(db.text("SELECT COUNT(*) FROM kmu_ems_data"))
        count = result.fetchone()[0]

        if count == 0:
            # 插入測試資料已在init.sql中完成
            print("kmu_ems_data table is empty, but test data should be inserted by init.sql")
        else:
            print(f"kmu_ems_data table already has {count} records, test data exists")

    except Exception as e:
        print(f"Error initializing test data: {e}")
        db.session.rollback()


def create_app():
    """做給main or app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # 初始化資料庫
    db.init_app(app)

    # 初始化預設用戶、設定表格和測試資料
    with app.app_context():
        init_default_users()
        init_settings_table()
        init_test_data()

    # 呼叫路由
    from .route.route import create_route
    create_route(app)

    return app