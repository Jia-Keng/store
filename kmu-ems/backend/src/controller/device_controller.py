from flask_restx import abort
from flask import request
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from src.util.modbus_collector import get_current_data, DEVICES, read_modbus


def log(msg):
    """輸出log"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


class DeviceController:
    """處理設備 HTTP 層"""

    @staticmethod
    def get_temperature_humidity():
        """取得溫濕度數據"""
        try:
            device_data = get_current_data()
            
            # 如果有資料庫資料，使用資料庫資料
            if device_data and not all(v is None for v in device_data.values()):
                return {
                    "device1": {
                        "temp": device_data.get("溫度01"),
                        "hum": device_data.get("濕度01")
                    },
                    "device2": {
                        "temp": device_data.get("溫度02"),
                        "hum": device_data.get("濕度02")
                    },
                    "doorSwitch": not bool(device_data.get("門禁")),
                    "UPS": {
                        "voltage": device_data.get("UPS電壓"),
                        "current": device_data.get("UPS電流")
                    }
                }
            
            # 沒有資料時返回測試資料
            return {
                "device1": {
                    "temp": 30.91,
                    "hum": 67.27
                },
                "device2": {
                    "temp": 23.27,
                    "hum": 66.25
                },
                "doorSwitch": True,
                "UPS": {
                    "voltage": 270.90,
                    "current": 0.0
                }
            }
                
        except Exception as e:
            print(f"modbus讀取失敗: {str(e)}")
            # 發生錯誤時也回傳測試資料
            return {
                "device1": {
                    "temp": 22.91,
                    "hum": 67.27
                },
                "device2": {
                    "temp": 23.27,
                    "hum": 66.25
                },
                "doorSwitch": True,
                "UPS": {
                    "voltage": 270.90,
                    "current": 0.0
                }
            }

