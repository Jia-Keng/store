from flask_restx import Namespace, Resource, fields
from config.swagger_config import create_api
from ..controller.device_controller import DeviceController
from ..controller.auth_controller import AuthController

def create_route(app):
    api = create_api(app)
    ns = Namespace('api', description='KMU EMS API', path='/api')
    api.add_namespace(ns)

    # 數據模型
    device_model = ns.model('Device', {
        'temp': fields.Float(description='溫度'),
        'hum': fields.Float(description='濕度')
    })
    
    ups_model = ns.model('UPS', {
        'voltage': fields.Float(description='UPS電壓'),
        'current': fields.Float(description='UPS電流')
    })
    
    temperature_humidity_model = ns.model('TemperatureHumidity', {
        'device1': fields.Nested(device_model, description='設備1數據'),
        'device2': fields.Nested(device_model, description='設備2數據'),
        'doorSwitch': fields.Boolean(description='門禁開關'),
        'UPS': fields.Nested(ups_model, description='UPS數據')
    })

    switch_model = ns.model('Switch', {
        'device_id': fields.Integer(required=True, description='設備ID')
    })

    # 認證模型
    login_model = ns.model('Login', {
        'username': fields.String(required=True, description='用戶名'),
        'password': fields.String(required=True, description='密碼')
    })

    setting_login_model = ns.model('SettingLogin', {
        'password': fields.String(required=True, description='設定密碼')
    })

    login_response_model = ns.model('LoginResponse', {
        'token': fields.String(description='JWT令牌'),
        'user': fields.String(description='用戶名'),
        'message': fields.String(description='響應訊息')
    })

    error_model = ns.model('Error', {
        'message': fields.String(description='錯誤訊息'),
        'error': fields.String(description='錯誤詳情')
    })

    # API 端點
    @ns.route('/TemperatureHumidity')
    class TemperatureHumidityAPI(Resource):
        @ns.response(200, 'Success', temperature_humidity_model)
        def get(self):
            """取得溫濕度數據"""
            return DeviceController.get_temperature_humidity()


    @ns.route('/health')
    class Health(Resource):
        def get(self):
            return {'status': 'healthy', 'message': 'Service is running'}


    # 認證 API
    @ns.route('/login')
    class LoginAPI(Resource):
        @ns.expect(login_model)
        @ns.response(200, 'Success', login_response_model)
        @ns.response(400, 'Bad Request', error_model)
        @ns.response(401, 'Unauthorized', error_model)
        @ns.response(500, 'Internal Server Error', error_model)
        def post(self):
            """用戶登入"""
            return AuthController.login()

    @ns.route('/settingLogin')
    class SettingLoginAPI(Resource):
        @ns.expect(setting_login_model)
        @ns.response(200, 'Success', login_response_model)
        @ns.response(400, 'Bad Request', error_model)
        @ns.response(401, 'Unauthorized', error_model)
        @ns.response(500, 'Internal Server Error', error_model)
        def post(self):
            """設定登入"""
            return AuthController.setting_login()

    setting_model = ns.model('Setting', {
        'temp1': fields.Raw(description='溫度1上下限'),
        'hum1': fields.Raw(description='濕度1上下限'),
        'temp2': fields.Raw(description='溫度2上下限'),
        'hum2': fields.Raw(description='濕度2上下限')
    })

    @ns.route('/setting')
    class Setting(Resource):
        @ns.response(200, 'Success', setting_model)
        @ns.response(400, 'Bad Request', error_model)
        @ns.response(401, 'Unauthorized', error_model)
        @ns.response(500, 'Internal Server Error', error_model)
        def get(self):
            """取得設定上下限數值"""
            return {
                "temp1": {
                    "upperLimit": 28.0,
                    "lowerLimit": 20.0
                },
                "hum1": {
                    "upperLimit": 68.0
                },
                "temp2": {
                    "upperLimit": 28.0,
                    "lowerLimit": 20.0
                },
                "hum2": {
                    "upperLimit": 68.0
                }
            }

    return api