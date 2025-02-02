from datetime import timedelta
from flask import Flask, send_from_directory
from routes import auth, prediction
from extensions import db, f_bcrypt, cors, jwt
import logging

app = Flask(__name__)

app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler("app.log")  # Log to a file
app.logger.addHandler(handler)

app.config.from_prefixed_env()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/mgram_dev"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_VERIFY_SUB"] = False  # Disable sub validation
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["UPLOAD_FOLDER"] = "uploads"

db.init_app(app)
jwt.init_app(app)
f_bcrypt.init_app(app)
cors.init_app(app)

app.register_blueprint(auth.bp)
app.register_blueprint(prediction.bp)


@app.route("/images/<string:name>")
def serve(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    app.run(debug=True)
