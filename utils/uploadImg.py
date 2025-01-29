import os
from CONSTANT import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        return os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    return False
