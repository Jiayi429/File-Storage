import os,mongo

from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS

def create_app():
	app = Flask(__name__)
	app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),"uploaded")
	app.config['ENCRYPT_FOLDER'] = os.path.join(os.path.dirname(__file__),"encrypted")
	app.config['DECRYPT_FOLDER'] = os.path.join(os.path.dirname(__file__),"decrypted")
	app.config['MONGO_URI'] = "mongodb://localhost:27017/filestorage"
	mongo = PyMongo(app)
	CORS(app)
return app