# Productivity Notes Backend

## Description

This is a Flask backend API for a notes app. Users can sign up,users can create, view, edit and delete their own notes. Users cannot see or change other users' notes.
 Passwords are hashed with bcrypt and are never stored as plain text.


## Installation

Uses Python 3.8.13 

1. Clone the repo:
   ```
   git clone https://github.com/edger-gesora/productivity-backend-app.git
   cd productivity-backend-app
   ```
2. Install the packages and open the virtual environment:
   ```
   pipenv install --dev
   pipenv shell
   ```
3. Create the database and add the starter data:
   ```
   cd server
   export FLASK_APP=app.py
   flask db upgrade head
   python seed.py
   ```
   The seed file creates two users: `alice` (password `alice123`) and `bob` (password `bob123`), each with two notes.

## Running the app

From the `server` folder:
```
python app.py
```
The API runs at http://localhost:5555

## Running the tests

From the `server` folder:
```
pytest -v
```
