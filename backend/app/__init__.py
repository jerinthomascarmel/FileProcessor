from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager  
from .routes.upload import upload_files  
from .routes.home import home  
from .routes.login import login  

def create_app():
    app = Flask(__name__)
    CORS(app)  
    
    # Configure your JWT secret key
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change to a secure key
    JWTManager(app)  # Initialize JWTManager with your app

    # Register routes
    app.add_url_rule('/', view_func=home)  # Add the home route
    app.add_url_rule('/upload', view_func=upload_files, methods=['POST'])  # Add the upload route
    app.add_url_rule('/login', view_func=login, methods=['POST'])  # Add the login route

    return app
