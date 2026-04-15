from app import create_app
from extensions import db, bcrypt
from models import Note, User


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(username="demo").first():
            print("Demo user already exists. Skipping seed.")
            return

        demo_password = bcrypt.generate_password_hash("password").decode("utf-8")
        demo = User(username="demo", password_digest=demo_password)
        db.session.add(demo)
        db.session.flush()

        notes = [
            Note(title="Morning journal", content="Today I completed the API lab.", mood="productive", owner=demo),
            Note(title="Workout plan", content="Chest and back workout for Tuesday.", mood="motivated", owner=demo),
            Note(title="Reading note", content="Finished a chapter on Flask security.", mood="focused", owner=demo),
        ]
        db.session.add_all(notes)
        db.session.commit()
        print("Seed data created.")


if __name__ == "__main__":
    seed()
