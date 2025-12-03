import time
import mysql.connector
from pymodbus.client import ModbusTcpClient
import schedule
from datetime import datetime
import os
import sys
import os
sys.path.append(os.path.dirname(__file__))
from threshold_monitor import check_and_alert

DB_CFG = {
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'), 
    'user': os.getenv('MYSQL_USER', 'root'), 
    'password': os.getenv('MYSQL_PASSWORD', 'root'), 
    'database': os.getenv('MYSQL_DATABASE', 'env_db')
}
TABLE = 'kmu_ems_data'
DEVICES = [
{"name": "溫度01", "ip": "10.253.254.7", "port": 502, "id": 1, "address": 1, "type": "int16", "endianness": "low", "scaling": 0.01, "register_type": "input"},
{"name": "濕度01", "ip": "10.253.254.7", "port": 502, "id": 1, "address": 0, "type": "int16", "endianness": "low", "scaling": 0.01, "register_type": "input"},
{"name": "溫度02", "ip": "10.253.254.7", "port": 503, "id": 1, "address": 1, "type": "int16", "endianness": "low", "scaling": 0.01, "register_type": "input"},
{"name": "濕度02", "ip": "10.253.254.7", "port": 503, "id": 1, "address": 0, "type": "int16", "endianness": "low", "scaling": 0.01, "register_type": "input"},
{"name": "門禁", "ip": "10.253.254.7", "port": 504, "id": 2, "address": 32, "register_type": "coil"},
{"name": "UPS電壓", "ip": "10.253.254.7", "port": 504, "id": 1, "address": 812, "type": "int16", "endianness": "low", "scaling": 0.1, "register_type": "holding"},
{"name": "UPS電流", "ip": "10.253.254.7", "port": 504, "id": 1, "address": 190, "type": "int16", "endianness": "low", "scaling": 0.1, "register_type": "holding"}
]


def read_modbus(client, dev):
    try:
        register_type = dev['register_type']
        addr = dev['address']
        slave = dev['id']

        if register_type == 'coil':
            result = client.read_coils(addr, count=1, slave=slave)
            if result.isError():
                return None
            return result.bits[0]
        elif register_type == 'input':
            func = client.read_input_registers
        else:  # holding
            func = client.read_holding_registers

        # 處理 int16
        result = func(addr, count=1, slave=slave)
        if result.isError():
            return None
            
        value = result.registers[0]
        
        return round(value * dev.get('scaling', 1.0), 2)

    except Exception as e:
        print(f"讀取錯誤 {dev['name']}: {e}")
        return None


def write_coil(ip, port, slave, address, value):
    try:
        client = ModbusTcpClient(ip, port=port, timeout=3)
        if not client.connect():
            return False
        
        result = client.write_coil(address, value, slave=slave)
        client.close()
        
        return not result.isError()
    except Exception as e:
        print(f"寫入錯誤: {e}")
        return False


def get_current_data():
    """從資料庫取得最新資料"""
    try:
        from setting import db
        
        query = f"SELECT * FROM `{TABLE}` ORDER BY timestamp DESC LIMIT 1"
        result = db.session.execute(db.text(query)).fetchone()
        
        if result:
            # 將結果轉換為字典格式
            columns = result._mapping.keys()
            data_dict = dict(zip(columns, result))
            
            # 按照 DEVICES 的順序映射數據
            data = {}
            for device in DEVICES:
                data[device['name']] = data_dict.get(device['name'])
            
            return data
        else:
            return {device['name']: None for device in DEVICES}
            
    except Exception as e:
        print(f"資料庫讀取錯誤: {e}")
        # 發生錯誤時嘗試從 modbus 讀取
        return collect()


def collect():
    data = {}
    groups = {}

    for d in DEVICES:
        key = (d['ip'], d['port'])
        if key not in groups:
            groups[key] = []
        groups[key].append(d)

    for (ip, port), devs in groups.items():
        client = ModbusTcpClient(ip, port=port, timeout=3)
        if not client.connect():
            print(f"連線失敗: {ip}:{port}")
            continue

        for d in devs:
            data[d['name']] = read_modbus(client, d)
            time.sleep(0.05)

        client.close()

    return data


def save_db(data):
    try:
        conn = mysql.connector.connect(**DB_CFG, charset='utf8mb4', collation='utf8mb4_unicode_ci')
        cur = conn.cursor()

        cols = ', '.join([f'`{d["name"]}` FLOAT' for d in DEVICES])
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS `{TABLE}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                {cols},
                INDEX(timestamp)
            )
        """)
        # replace(second=0, microsecond=0)
        now = datetime.now()
        col_names = ', '.join([f'`{d["name"]}`' for d in DEVICES])
        placeholders = ', '.join(['%s'] * (len(DEVICES) + 1))

        cur.execute(
            f"INSERT INTO `{TABLE}` (timestamp, {col_names}) VALUES ({placeholders})",
            [now] + [data.get(d['name']) for d in DEVICES]
        )

        conn.commit()
        print(f"DB: {now}")
        conn.close()

    except Exception as e:
        print(f"DB err: {e}")


def job():
    data = collect()
    save_db(data)
    check_and_alert()


if __name__ == '__main__':
    print("啟動中...")
    schedule.every(00).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)