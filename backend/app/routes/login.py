from flask import request, jsonify
from flask_jwt_extended import create_access_token
from ..user_data import users  # Import the users list

def login():
    try:
        # Parse the incoming JSON request for username and password
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        user = None   
        for userModel in users:
            if userModel['username'] == username:
                user = userModel
        
        if not user:
            return jsonify({"error": "Authentication failed"}), 401

        # Check if the password matches (without hashing)
        if password != user['password']:
            return jsonify({"error": "Authentication failed"}), 401

        # Create a JWT token for the user
        token = create_access_token(identity=user['username'])  # Use the username as the identity

        # Return the JWT token
        return jsonify({"token": token}), 200

    except Exception as e:
        print(f'{str(e)}')
        return jsonify({"error": "Login failed"}), 500
