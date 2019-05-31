import os
import time
import hashlib
import json
import mongo
import shutil
import filecmp

from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),"uploaded")
app.config['MONGO_URI'] = "mongodb://localhost:27017/filestorage"
mongo = PyMongo(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['GET','POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")
	"""
	for i in range(0,len(uploaded_files)-1):
		for j in range(i,len(uploaded_files)):
			if filecmp.cmp(uploaded_files[i],uploaded_files[j],shallow=True):
				os.remove(uploaded_files[i])
	"""
	filenames = []
	#res = []
	
	for file in uploaded_files:
		flag = 1
		filename = secure_filename(file.filename)
		file_path = os.path.join(os.path.dirname(__file__),"temp",filename)
		desDir = os.path.join(app.config['UPLOAD_FOLDER'],filename)
		if not os.path.exists(desDir):
			file.save(file_path)
			file_hash = getHash(file_path)


			if mongo.db.files.find_one({'hash':file_hash}):
				flag = 0
				os.remove(file_path)

			if flag:
				filenames.append(filename)
				s = {}
				s['hash'] = file_hash
				s['name'] = os.path.splitext(filename)[0]
				s['path'] = file_path
				s['extension'] = os.path.splitext(filename)[1]
				s['size'] = str(os.stat(file_path).st_size)+" bytes"
				s['creatDate'] = time.ctime(os.path.getctime(file_path)) 
				s['modifyDate'] = time.ctime(os.path.getmtime(file_path))
			#res.append(s)
		#print(s)
	#json.dumps(res,indent=4,separators=(',',':'))
				mongo.db.files.insert_one(s)
				shutil.move(file_path,desDir)

	return render_template('upload.html', filenames = filenames)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

#return the hash value of file
def getHash(filepath):
	#BLOCKSIZE = 65536
	hashvalue = {}
	h1 = hashlib.sha1()
	h2 = hashlib.sha256()
	h3 = hashlib.sha384()
	h4 = hashlib.sha512()
	h5 = hashlib.md5()
	b = bytearray(128*1024)
	mv = memoryview(b)
	with open(filepath,'rb',buffering = 0) as f:
		for n in iter(lambda:f.readinto(mv),0):
			h1.update(mv[:n])
			h2.update(mv[:n])
			h3.update(mv[:n])
			h4.update(mv[:n])
	hashvalue['sha128'] = h1.hexdigest()
	hashvalue['sha256'] = h2.hexdigest()
	hashvalue['sha384'] = h3.hexdigest()
	hashvalue['sha512'] = h4.hexdigest()
	hashvalue['md5'] = h5.hexdigest()
	return hashvalue

if __name__ == '__main__':
	app.run(debug = True)