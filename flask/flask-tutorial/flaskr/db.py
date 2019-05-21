
from flask.cli import with_appcontext
#the connection is stored and reused instead of creating a new one if get_db is called for a second time in the same request
from flask import current_app,g
import click
import sqlite3

def init_db():
	db = get_db()
	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
	init_db()
	click.echo('Initialized the database.')

def init_app(app):
	app.teardown_appcontext(close_db)
	#let Flask to call the function when cleaning up after return the response
	app.cli.add_command(init_db_command)
	#adds a new command that can be called with the flask command

def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(
			#establish a connection to the file pointed at by the DATABASE configuration key
			current_app.config['DATABASE'],
			#c_a is a special object that points to the Flask app handling the request
			detect_types = sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	db = g.pop('db',None)
	if db is not None:
		db.close()