import os
import json
import hashlib
import time

filename = "samplefile.txt"
temp = {}
result = []

#read the file contents and return
def readFile(filename):
	filehandle = open(filename,"r")
	file_content = filehandle.read()
	filehandle.close()
	return file_content

#return the hash value of file
def getHash(filename):
	#BLOCKSIZE = 65536

	h1 = hashlib.sha1()
	h2 = hashlib.sha256()
	h3 = hashlib.sha384()
	h4 = hashlib.sha512()
	b = bytearray(128*1024)
	mv = memoryview(b)
	with open(filename,'rb',buffering = 0) as f:
		for n in iter(lambda:f.readinto(mv),0):
			h1.update(mv[:n])
			h2.update(mv[:n])
			h3.update(mv[:n])
			h4.update(mv[:n])
	return [h1.hexdigest(),h2.hexdigest(),h3.hexdigest(),h4.hexdigest()]

#return the extension of file
def getExt(filename):
	start, ext = os.path.splitext(filename)
	return ext



parDir = os.getcwd()
desDir = os.path.join(parDir,"uploaded","output.json")

temp['name'] = os.path.splitext(filename)[0]
temp['path'] = os.getcwd()
temp['extension'] = getExt(filename)
temp['content'] = readFile(filename)
temp['size'] = os.stat(filename).st_size
temp['creatDate'] = time.ctime(os.path.getctime(filename))
temp['modifyDate'] = time.ctime(os.path.getmtime(filename))
temp['hash'] = getHash(filename)
result.append(temp)
output = open(desDir,"w")
json.dump(result,output, indent=4, separators=(',',': '))

output.close()

