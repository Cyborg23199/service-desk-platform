from flask import Flask
from flasgger import Swagger
from config import Config
from models import db
from api import api_bp
from web import web_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuration of Swagger UI:
    app.config['SWAGGER'] = {
        'title': 'Service Desk API',
        'uiversion': 3,
        'description': 'OpenAPI / Swagger documentation for Service Desk Platform REST API'
    }

    db.init_app(app)
    Swagger(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)