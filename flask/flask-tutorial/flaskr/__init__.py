import os
from flask import Flask

#application factory,registered configuration,url
def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	#the configuration files are relative to the instance folder
	app.config.from_mapping(
		SECRET_KEY='dev',
		#keep data safe, should be overriden with a random value when deploying
		DATABASE=os.path.join(app.instance_path,'flaskr.sqlite'),
	)

	if test_config is None:
		app.config.from_pyfile('config.py',silent=True)
	else:
		app.config.from_mapping(test_config)

	try:
		os.makedirs(app.instance_path)
		#ensures the app.instance_path exists
	except OSError:
		pass

	@app.route('/hello')
	def hello():
		return 'Hello, World'

	from . import db
	db.init_app(app)

	from . import auth, blog
	app.register_blueprint(auth.bp)
	app.register_blueprint(blog.bp)
	app.add_url_rule('/', endpoint='index')

	return app
