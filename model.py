from extensions import db, f_bcrypt
from CONSTANT import DEFAULT_PASSWORD


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(
        db.Enum("USER", "ADMIN", name="user_roles"), default="USER", nullable=False
    )
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(
        db.String(255),
        nullable=False,
        default=f_bcrypt.generate_password_hash(DEFAULT_PASSWORD),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "password" not in kwargs:
            self.password = f_bcrypt.generate_password_hash(DEFAULT_PASSWORD)


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ic_no = db.Column(db.String(12), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship("User", backref="prediction")
    images = db.relationship("BIRADSImage", backref="prediction")


class BIRADSImage(db.Model):
    __tablename__ = "birads_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img_name = db.Column(db.Text, nullable=False)
    prediction_id = db.Column(
        db.Integer, db.ForeignKey("predictions.id"), nullable=False
    )
    result = db.Column(db.String(10), nullable=False)

    img_prediction = db.relationship("Prediction", backref="image")


class BIRADSPrediction(db.Model):
    __tablename__ = "birads_predictions"
    birads_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img_id = db.Column(db.Integer, db.ForeignKey("birads_images.id"), nullable=False)
    birads_category = db.Column(db.String(10), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)

    image = db.relationship("BIRADSImage", backref="biradPrediction")
