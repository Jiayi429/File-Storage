import pytest
from . import create_app



#test all routes if their status code is 200
def test_home_page(client):
	response = client.get('/')
	assert response.status_code == 200

@pytest.fixture
def app():
	app = create_app()
	return app