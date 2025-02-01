from app import app, db
from model import User


def seed_db():
    db.create_all()
    admin = User(
        email="admin@mgram.com", name="Fulan", phone_no="0123456789", role="ADMIN"
    )
    user = User(email="ahmad@mgram.com", name="Ahmad", phone_no="0123456788")

    db.session.add(admin)
    db.session.add(user)
    db.session.commit()


with app.app_context():
    seed_db()
