import os, random, struct
import time
import hashlib
import json
import mongo
import shutil
import filecmp
import pagination

from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_pymongo import PyMongo
from Crypto.Cipher import AES
from falsk_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),"uploaded")
app.config['ENCRYPT_FOLDER'] = os.path.join(os.path.dirname(__file__),"encrypted")
app.config['MONGO_URI'] = "mongodb://localhost:27017/filestorage"
mongo = PyMongo(app)
CORS(app)

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
				s['hash'] = file_hash
				s['name'] = os.path.splitext(filename)[0]
				s['path'] = file_path
				s['extension'] = os.path.splitext(filename)[1]
				s['size'] = str(os.stat(file_path).st_size)+" bytes"
				s['creatDate'] = time.ctime(os.path.getctime(file_path)) 
				s['modifyDate'] = time.ctime(os.path.getmtime(file_path))
				#res.append(filename,s)
		#print(s)
	#json.dumps(res,indent=4,separators=(',',':'))
				mongo.db.files.insert_one(s)
				shutil.move(file_path,desDir)
				key = ''.join(chr(random.randint(0,0xFF)) for i in range(16))
				encrypt_file(key, file_path)
	#mongo.db.files.insert_many(res)

	return render_template('upload.html', filenames = filenames, listlen = len(filenames),hashvals = res)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/explorer', methods = ['GET','POST'])
#TODO: display all uploaded files and hashes256 with decrypt button
#	   display filenames by pagination
def explor_files():

	names = list(mongo.db.files.find({name:1}))
	hashes = list(mongo.db.files.find({hash:1}).sha256)
	pager_obj = pagination(request.args.get("page",1),len(names),request.path,request.args,per_page_count = 10)
	name_list = names[pager_obj.start:pager_obj.end]
	hash_list = hashes[pager_obj.start:pager_obj.end]
	html = pager_obj.page_html()

	return render_template('explor.html',names = name_list, hashes = hash_list)


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

def encrypt_file(key, in_file, out_file=None, chunksize = 64*1024):
	#get the sha256 value from mongodb to name outfile
	fn = mongo.db.files.find({'name':in_file},{hash:1}).sha256

	if not out_file:
		out_file = fn + '.enc'

	iv = ''.join(chr(random.randint(0,0xFF)) for i in range(16))
	encryptor = AES.new(key,AES.MODE_CBC,iv)
	filesize = os.path.getsize(in_file)

	with open(in_file,'rb') as infile:
		with open(out_file,'wb') as outfile:
			outfile.write(struct.pack('<Q',filesize))
			outfile.write(iv)

			while True:
				chunk = infile.read(chunksize)
				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - len(chunk)%16)
				outfile.write(encryptor.encrypt(chunk))
	outfile.save(os.path.join(app.config['ENCRYPT_FOLDER'],out_file))

def decrypt_file(key, in_file, out_file=None, chunksize=24*1024):
	if not out_file:
		out_file = in_file+'dec'
	with open(in_file,'rb') as infile:
		origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
		iv = infile.read(16)
		decryptor = AES.new(key,AES.MODE_CBC,iv)

		with open(out_file,'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)
				if len(chunk) == 0:
					break
				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(origsize)

if __name__ == '__main__':
	app.run(debug = True)