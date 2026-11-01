#!/usr/bin/env python3

from app import app
from models import db, User, Note

with app.app_context():
    # Seeds info

    Note.query.delete()
    User.query.delete()

    alice = User(username='alice')
    alice.password_hash = 'alice123'
    bob = User(username='bob')
    bob.password_hash = 'bob123'
    db.session.add_all([alice, bob])
    db.session.commit()

    notes = [
        Note(title='Shopping list', content='Milk, eggs, bread', category='personal', user_id=alice.id),
        Note(title='Study plan', content='Review Flask routes tonight', category='school', user_id=alice.id),
        Note(title='Gym', content='Leg day on Monday', category='health', user_id=bob.id),
        Note(title='Project idea', content='Build a budget tracker', category='school', user_id=bob.id),
    ]
    db.session.add_all(notes)
    db.session.commit()

    print('Database seeded')