from flask import jsonify

def home():
    return jsonify({"message": "Welcome to the File Processor API!"})
