from app import app, db
from model import User


def seed_db():
    db.create_all()
    admin = User(
        email="admin@mgram.net", name="Super Admin", phone_no="0123456789", role="ADMIN"
    )
    user = User(email="ahmad@mgram.net", name="Ahmad", phone_no="0123456788")

    db.session.add(admin)
    db.session.add(user)
    db.session.commit()


with app.app_context():
    seed_db()
