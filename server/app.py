from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, bcrypt, User, Note

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'change-this-secret-key'

migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 422

    try:
        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 422
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already taken'}), 422

    session['user_id'] = user.id
    return jsonify({'id': user.id, 'username': user.username}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.authenticate(data.get('password')):
        session['user_id'] = user.id
        return jsonify({'id': user.id, 'username': user.username}), 200

    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    return {}, 204


@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'id': user.id, 'username': user.username}), 200


# This is where Notes routes will be 
def current_user():
    """Return the logged-in user, or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


@app.route('/notes', methods=['GET'])
def get_notes():
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    notes = Note.query.filter_by(user_id=user.id).all()
    return jsonify([note.to_dict() for note in notes]), 200


@app.route('/notes', methods=['POST'])
def create_note():
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 422

    try:
        note = Note(
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category', 'general'),
            user_id=user.id,
        )
        db.session.add(note)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 422

    return jsonify(note.to_dict()), 201


@app.route('/notes/<int:id>', methods=['PATCH'])
def update_note(id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    note = db.session.get(Note, id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    if note.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    try:
        for field in ['title', 'content', 'category']:
            if field in data:
                setattr(note, field, data[field])
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'error': str(err)}), 422

    return jsonify(note.to_dict()), 200


@app.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    note = db.session.get(Note, id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    if note.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(note)
    db.session.commit()
    return {}, 204
  
if __name__ == '__main__':
    app.run(port=5555, debug=True)