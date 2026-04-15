# Flask Notes API Backend

A JWT-based Flask backend for a user-owned note tracking app.

## Features

- User registration and login
- Password hashing with Flask-Bcrypt
- JWT authentication with Flask-JWT-Extended
- User-owned `notes` resource with full CRUD
- Pagination support for note listing
- SQLAlchemy models and Flask-Migrate migrations
- Seed script with sample user and notes

## Quick start

1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

2. Initialize the database

```bash
export FLASK_APP=manage.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

3. Seed sample data

```bash
python seed.py
```

4. Run the app

```bash
python app.py
```

## API endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/profile`
- `GET /notes?page=1&per_page=10`
- `POST /notes`
- `GET /notes/<note_id>`
- `PUT /notes/<note_id>`
- `DELETE /notes/<note_id>`

## Notes

- The app is configured to use a local SQLite database by default.
- Set `DATABASE_URL` and `JWT_SECRET_KEY` in the environment for production usage.
