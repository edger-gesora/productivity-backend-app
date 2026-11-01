from flask import Flask
from flask_migrate import Migrate

from models import db, bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'change-this-secret-key'

migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)

# Routes info

if __name__ == '__main__':
    app.run(port=5555, debug=True)