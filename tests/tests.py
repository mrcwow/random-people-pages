import pytest
from unittest.mock import patch, MagicMock
import mongomock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    with patch("app.MongoClient", return_value=mongomock.MongoClient()):
        app.config["TESTING"] = True
        app.users_collection = mongomock.MongoClient().db.collection
        
        app.users_collection.delete_many({})
        
        with app.test_client() as client:
            yield client
            
        app.users_collection.delete_many({})

randomuser_data = {
    "results": [
        {
        "gender": "female",
        "name": {
            "title": "Miss",
            "first": "Jennie",
            "last": "Nichols"
        },
        "location": {
            "street": {
            "number": 8929,
            "name": "Valwood Pkwy",
            },
            "city": "Billings",
            "state": "Michigan",
            "country": "United States",
            "postcode": "63104",
            "coordinates": {
            "latitude": "-69.8246",
            "longitude": "134.8719"
            },
            "timezone": {
            "offset": "+9:30",
            "description": "Adelaide, Darwin"
            }
        },
        "email": "jennie.nichols@example.com",
        "login": {
            "uuid": "7a0eed16-9430-4d68-901f-c0d4c1c3bf00",
            "username": "yellowpeacock117",
            "password": "addison",
            "salt": "sld1yGtd",
            "md5": "ab54ac4c0be9480ae8fa5e9e2a5196a3",
            "sha1": "edcf2ce613cbdea349133c52dc2f3b83168dc51b",
            "sha256": "48df5229235ada28389b91e60a935e4f9b73eb4bdb855ef9258a1751f10bdc5d"
        },
        "dob": {
            "date": "1992-03-08T15:13:16.688Z",
            "age": 30
        },
        "registered": {
            "date": "2007-07-09T05:51:59.390Z",
            "age": 14
        },
        "phone": "(272) 790-0888",
        "cell": "(489) 330-2385",
        "id": {
            "name": "SSN",
            "value": "405-88-3636"
        },
        "picture": {
            "large": "https://randomuser.me/api/portraits/men/75.jpg",
            "medium": "https://randomuser.me/api/portraits/med/men/75.jpg",
            "thumbnail": "https://randomuser.me/api/portraits/thumb/men/75.jpg"
        },
        "nat": "US"
        }
    ],
    "info": {
        "seed": "56d27f4a53bd5441",
        "results": 1,
        "page": 1,
        "version": "1.4"
    }
}

def requests_mock_get(*args, **kwargs):
    mock_response = MagicMock()
    mock_response.json.return_value = randomuser_data
    mock_response.raise_for_status = lambda: None
    return mock_response

@patch("app.requests.get", side_effect=requests_mock_get)
def test_index_redirect(mock_get, client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/homepage" in response.location

@patch("app.requests.get", side_effect=requests_mock_get)
def test_get_homepage(mock_get, client):
    response = client.get("/homepage")
    assert response.status_code == 200
    assert b"<table" in response.data

@patch("app.requests.get", side_effect=requests_mock_get)
def test_add_users(mock_get, client):
    response = client.post("/homepage", data={"add_num": "1"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"jennie.nichols@example.com" in response.data

    user = app.users_collection.find_one({"login.uuid": "7a0eed16-9430-4d68-901f-c0d4c1c3bf00"})
    assert user is not None
    assert user["email"] == "jennie.nichols@example.com"

@patch("app.requests.get", side_effect=requests_mock_get)
def test_page_pagination(mock_get, client):
    client.post("/homepage", data={"add_num": "15"}, follow_redirects=True)
    response = client.post("/homepage", data={"page_to_go": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"<table" in response.data

@patch("app.requests.get", side_effect=requests_mock_get)
def test_get_user_by_id(mock_get, client):
    client.post("/homepage", data={"add_num": "1"}, follow_redirects=True)
    user_id = "7a0eed16-9430-4d68-901f-c0d4c1c3bf00"
    response = client.get(f"/homepage/{user_id}")
    assert response.status_code == 200
    assert b"jennie.nichols@example.com" in response.data

@patch("app.requests.get", side_effect=requests_mock_get)
def test_get_random_user(mock_get, client):
    client.post("/homepage", data={"add_num": "10"}, follow_redirects=True)
    response = client.get("/homepage/random")
    assert response.status_code == 200
    assert b"User Page" in response.data and b"jennie.nichols@example.com" in response.data