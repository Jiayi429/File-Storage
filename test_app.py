import pytest
from . import create_app
from flask import url_for


#test all routes if their status code is 200
def test_home_page(client):
	response = client.get('/')
	assert response.status_code == 200

def test_upload_page(client):
	response = client.post('/upload')
	assert response.status_code == 200

def test_uploads_page(client):
	response = client.get('/uploads')
	assert response.status_code == 200

def test_explorer_page(client):
	response = client.get('/explorer')
	assert response.status_code == 200

def test_decrypted_page(client):
	response = client.get('/decrypted')
	assert response.status_code == 200

@pytest.mark.options(debug=False)
def test_app(app):
  assert not app.debug

def test_app(client):
    assert client.get(url_for('uploaded_files')).status_code == 200
    assert client.get(url_for('explor_files')).status_code == 200
    assert client.get(url_for('decrypted')).status_code == 200
    assert client.get(url_for('upload')).status_code == 200

def test_server_is_up_and_running(self):
        res = urllib2.urlopen(url_for('index', _external=True))
        assert res.code == 200

@pytest.fixture
def app():
	app = create_app()
	return app