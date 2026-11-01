import random
import pytest

from app import app
from models import db, User

def make_client():
    app.config['TESTING'] = True
    return app.test_client()

def new_name():
    return 'user' + str(random.randint(1000, 999999))

@pytest.fixture(scope='module', autouse=True)
def clean_up():
    yield
    # remove the users these tests created
    with app.app_context():
        for user in User.query.filter(User.username.like('user%')).all():
            db.session.delete(user)
        db.session.commit()

def test_signup_returns_201():
    client = make_client()
    res = client.post('/signup', json={'username': new_name(), 'password': 'pass123'})
    assert res.status_code == 201

def test_duplicate_username_returns_422():
    client = make_client()
    name = new_name()
    client.post('/signup', json={'username': name, 'password': 'pass123'})
    res = client.post('/signup', json={'username': name, 'password': 'pass123'})
    assert res.status_code == 422

def test_login_with_wrong_password_returns_401():
    client = make_client()
    name = new_name()
    client.post('/signup', json={'username': name, 'password': 'pass123'})
    res = client.post('/login', json={'username': name, 'password': 'wrong'})
    assert res.status_code == 401

def test_check_session_before_and_after_login():
    client = make_client()
    assert client.get('/check_session').status_code == 401
    client.post('/signup', json={'username': new_name(), 'password': 'pass123'})
    assert client.get('/check_session').status_code == 200

def test_logout_returns_204():
    client = make_client()
    client.post('/signup', json={'username': new_name(), 'password': 'pass123'})
    assert client.delete('/logout').status_code == 204
    assert client.get('/check_session').status_code == 401

def test_notes_need_login():
    client = make_client()
    assert client.get('/notes').status_code == 401
    assert client.post('/notes', json={'title': 'a', 'content': 'b'}).status_code == 401

def test_note_create_update_delete():
    client = make_client()
    client.post('/signup', json={'username': new_name(), 'password': 'pass123'})

    res = client.post('/notes', json={'title': 'Test', 'content': 'Hello'})
    assert res.status_code == 201
    note_id = res.get_json()['id']

    assert client.get('/notes').status_code == 200
    assert client.patch('/notes/' + str(note_id), json={'title': 'New'}).status_code == 200
    assert client.delete('/notes/' + str(note_id)).status_code == 204

def test_user_cannot_edit_someone_elses_note():
    owner = make_client()
    owner.post('/signup', json={'username': new_name(), 'password': 'pass123'})
    note_id = owner.post('/notes', json={'title': 'Mine', 'content': 'Private'}).get_json()['id']

    other = make_client()
    other.post('/signup', json={'username': new_name(), 'password': 'pass123'})
    assert other.patch('/notes/' + str(note_id), json={'title': 'Hack'}).status_code == 403
    assert other.delete('/notes/' + str(note_id)).status_code == 403