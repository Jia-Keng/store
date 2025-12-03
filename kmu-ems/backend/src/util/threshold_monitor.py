import mysql.connector
import requests
import time
import json
import os
import logging
from datetime import datetime

# 設定日誌
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'threshold_monitor.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_and_alert():
    try:
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        db_config = config.get('database', {
            'host': 'localhost', 'user': 'root', 'password': 'root', 'database': 'env_db'
        })
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT `溫度01`, `濕度01`, `UPS電壓`, `UPS電流`, `門禁`
            FROM kmu_ems_data ORDER BY timestamp DESC LIMIT 1
        """)
        data = cursor.fetchone()
        conn.close()
        
        if not data:
            logger.info("資料庫中無資料")
            return
        
        logger.info(f"檢查資料: 溫度={data[0]}°C, 濕度={data[1]}%, 電壓={data[2]}V, 電流={data[3]}A, 門禁={data[4]}")
    
        temp, hum, voltage, current, door = data
        thresholds = config['thresholds']
        alerts = []
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        if temp and temp > thresholds['temperature']['max']:
            alerts.append(f"{now} 溫度過高: {temp}°C")
        if hum and hum > thresholds['humidity']['max']:
            alerts.append(f"{now} 濕度過高: {hum}%")
        if voltage and voltage > thresholds['voltage']['max']:
            alerts.append(f"{now} 電壓異常: {voltage}V")
        if current and current > thresholds['current']['max']:
            alerts.append(f"{now} 電流過載: {current}A")
        if door == 1:
            alerts.append(f"{now} 人員進出")
        
        for alert in alerts:
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{config['bot_token']}/sendMessage",
                    data={"chat_id": config['chat_id'], "text": f"{config.get('site_name', 'KMU-EMS')}\n{alert}"},
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info(f"Telegram通知發送成功: {alert}")
                else:
                    logger.error(f"Telegram通知發送失敗 ({response.status_code}): {alert}")
            except Exception as e:
                logger.error(f"發送Telegram通知時發生錯誤: {e}")
        
        if not alerts:
            logger.info("所有數值正常，無需警報")
            
    except Exception as e:
        logger.error(f"監控檢查時發生錯誤: {e}")

def monitor_loop(interval=60):
    logger.info(f"開始監控，檢查間隔: {interval}秒")
    while True:
        try:
            check_and_alert()
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("監控程式已停止")
            break
        except Exception as e:
            logger.error(f"監控迴圈發生錯誤: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    monitor_loop(60)