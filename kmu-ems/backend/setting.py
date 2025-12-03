import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Config:
    # SQLAlchemy 配置
    from urllib.parse import quote_plus
    password = quote_plus(os.getenv('MYSQL_PASSWORD', 'root'))
    mysql_host = os.getenv('MYSQL_HOST') or 'localhost'
    mysql_port = os.getenv('MYSQL_PORT') or 3306
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER', 'root')}:{password}@{mysql_host}:{mysql_port}/{os.getenv('MYSQL_DATABASE', 'env_db')}?charset=utf8mb4&collation=utf8mb4_unicode_ci&use_unicode=true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    設定SQLAlchemy與資料庫之間的連線
    Flask在運作一段時間後，常會出現：
    MySQL/MariaDB 自動斷線（空閒太久）
    資料庫連線回收不正常
    Too many connections
    OperationalError: MySQL server has gone away
    連線池滿了導致請求卡死

    pool_pre_ping: True 在每次使用連線前先測試連線是否還活著
    pool_recycle: 300  5分鐘後自動回收連線
    pool_timeout: 20  當連線池滿了，等待 20 秒後如果仍無可用連線就丟錯
    max_overflow: 0  不允許超出連線池的額外連線
    """
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 5,
        'pool_size': 10,
        'max_overflow': 5
    }


    # 支援中文
    JSON_AS_ASCII = False
    
    # JWT Secret Key
    SECRET_KEY = os.getenv('SECRET_KEY', 'kmu-ems-secret-key-2024')


