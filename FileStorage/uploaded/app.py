import os, random, struct
import time
import hashlib
import json
import mongo
import shutil
import filecmp

from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_pymongo import PyMongo
from Crypto.Cipher import AES
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),"uploaded")
app.config['ENCRYPT_FOLDER'] = os.path.join(os.path.dirname(__file__),"encrypted")
app.config['DECRYPT_FOLDER'] = os.path.join(os.path.dirname(__file__),"decrypted")

app.config['MONGO_URI'] = "mongodb://localhost:27017/filestorage"
mongo = PyMongo(app)
CORS(app)
key = 'keyskeyskeyskeys'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['GET','POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")

	filenames = []
	res = []
	
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
				res.append(file_hash)
				os.remove(file_path)

			if flag:
				filenames.append(filename)
				s = {}
				filesize = os.stat(file_path).st_size
				s['hash'] = file_hash
				s['name'] = os.path.splitext(filename)[0]
				s['path'] = desDir
				s['extension'] = os.path.splitext(filename)[1]
				s['size'] = str(filesize)+" bytes"
				s['creatDate'] = time.ctime(os.path.getctime(file_path)) 
				s['modifyDate'] = time.ctime(os.path.getmtime(file_path))

				mongo.db.files.insert_one(s)
				shutil.move(file_path,desDir)
				encrypt_file(key,s['hash']['sha256'],filesize,desDir)
	count = len(list(mongo.db.files.find()))

	return render_template('upload.html', filenames = filenames, listlen = len(filenames),hashvals = res,count= count)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/explorer', methods = ['GET','POST'])

def explor_files():
	#while total_count > 10:
	docs = mongo.db.files.find().limit(10)

	name_list = []
	hash_list = []
	for doc in list(docs):
		name_list.append(doc['name'])
		hash_list.append(doc['hash']['sha256'])

	return render_template('explor.html',name = name_list, hash = hash_list, items = len(name_list))

@app.route('/decrypted', methods = ['GET','POST'])
def decrypted():
	if request.method == 'GET':
		file_hash = request.args.get('file_hash')


		fn = mongo.db.files.find_one({'sha256':file_hash},{'name':1})

		ext = mongo.db.files.find_one({'sha256':file_hash},{'extension':1})
		des_file = str(file_hash) + '.enc'
		des_path = os.path.join(app.config['ENCRYPT_FOLDER'],des_file)
		
		out_file = str(fn['name'])+'.'+str(ext['extension'])
		out_path = out_path = os.path.join(app.config['DECRYPT_FOLDER'],out_file)
		decrypt_file(key, des_path,out_path)

		return send_from_directory(app.config['DECRYPT_FOLDER'],out_file, as_attachment=True)

def encrypt_file(key,file_hash,size,path):
	chunksize = 64*1024
	out_file = str(file_hash) + '.enc'
	iv = ''.join(chr(random.randint(0,0xFF)) for i in range(16))
	encryptor = AES.new(key,AES.MODE_CBC,iv)
	filesize = size
	out_path = os.path.join(app.config['ENCRYPT_FOLDER'],out_file)

	with open(path,'rb') as infile:
		with open(out_path,'wb') as outfile:
			outfile.write(struct.pack('<Q',filesize))
			outfile.write(iv)

			while True:
				chunk = infile.read(chunksize)
				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - len(chunk)%16)
				outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key,in_path,out_path):

	chunksize=24*1024
	#out_file = in_file+'dec'
	#out_path = out_path = os.path.join(app.config['DECRYPT_FOLDER'],out_file)

	with open(in_path,'rb') as infile:
		origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
		iv = infile.read(16)
		decryptor = AES.new(key,AES.MODE_CBC,iv)

		with open(out_path,'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)
				if len(chunk) == 0:
					break
				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(origsize)


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