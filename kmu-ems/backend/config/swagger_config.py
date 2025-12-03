from flask_restx import Api


def create_api(app):
    """swagger auth 功能"""
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT token in format: Bearer <token>'
        }
    }

    return Api(
        app,
        version='1.0',
        title='高雄醫學大學後端API',
        description='高雄醫學大學後端 API',
        doc='/api/docs/',
        authorizations=authorizations,
        security='Bearer',
        ui_strings={
            'Schema'
        }
    )