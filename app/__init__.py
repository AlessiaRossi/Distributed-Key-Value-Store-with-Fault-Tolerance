from flask import Flask

def create_app(config):
    app = Flask(__name__)
    with app.app_context():
        from .routes import register_routes
        register_routes(app, config)
    return app
