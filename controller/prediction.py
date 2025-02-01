from flask import request, current_app
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Prediction, BIRADSImage, BIRADSPrediction
from extensions import db
from utils.mgram_v2 import predict_image
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import os

parser = reqparse.RequestParser()
parser.add_argument("ic_no", type=str, help="help")
predictionFields = {
    "id": fields.String,
    "icNo": fields.String(attribute="ic_no"),
    "timestamp": fields.String(attribute="created_at"),
}


def preprocess(files):
    images = []
    for file in files:
        img = Image.open(file.stream).convert("RGB")
        img_array = np.array(img)
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        images.append((img_tensor, file.filename))

    return predict_image(images)


class PredictImage(Resource):
    @jwt_required()
    @marshal_with(predictionFields)
    def get(self):
        predictions = Prediction.query.all()
        return predictions, 200

    @jwt_required()
    def post(self):
        if "birad_images" not in request.files:
            return "empty", 400

        files = request.files.getlist("birad_images")
        predictions = preprocess(files)

        return predictions, 201


class SavePrediction(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()

        if "birad_images" not in request.files:
            return "empty", 400

        files = request.files.getlist("birad_images")
        ic_no = request.form.get("ic_no")

        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

        predictions = preprocess(files)
        # response = [
        #     {
        #         "name": "birads10.jpg",
        #         "biradPrediction": [
        #             {"birad": "BIRADS1", "accuracy": 47.54},
        #             {"birad": "BIRADS3", "accuracy": 17.49},
        #             {"birad": "BIRADS4", "accuracy": 17.49},
        #             {"birad": "BIRADS5", "accuracy": 17.49},
        #         ],
        #         "highest": "BIRADS1",
        #     }
        #     ...
        # ]

        # save to db
        new_prediction = Prediction(user_id=current_user["id"], ic_no=ic_no)
        db.session.add(new_prediction)

        for pred in predictions:
            x = BIRADSImage(
                img_name=pred["name"],
                img_prediction=new_prediction,
                result=pred["highest"],
            )
            db.session.add(x)

            for birad in pred["biradPrediction"]:
                y = BIRADSPrediction(
                    birads_category=birad["birad"], accuracy=birad["accuracy"], image=x
                )
                db.session.add(y)

        db.session.commit()

        return {"message": "Prediction stored successfully"}, 201


detailPrediction = {
    **predictionFields,
    "images": fields.Nested(
        {
            "id": fields.String,
            "name": fields.String(attribute="img_name"),
            "highest": fields.String(attribute="result"),
            "biradPrediction": fields.Nested(
                {
                    "id": fields.String(attribute="birads_id"),
                    "birad": fields.String(attribute="birads_category"),
                    "accuracy": fields.Float,
                }
            ),
        }
    ),
}


class ViewPrediction(Resource):
    @jwt_required()
    @marshal_with(detailPrediction)
    def get(self, id):
        prediction = Prediction.query.filter_by(id=id).first()
        return prediction, 200
