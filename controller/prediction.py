from flask import request, jsonify, current_app
from flask_restful import Resource, reqparse, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Prediction, BIRADSImage, BIRADSPrediction
from extensions import db
from utils.uploadImg import upload
from utils.mgram_v2 import predict_image
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import os

parser = reqparse.RequestParser()
parser.add_argument("ic_no", type=str, help="help")
predictFields = {"ic_no": fields.String}


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
    def post(self):
        if "birad_images" not in request.files:
            return "empty", 400

        files = request.files.getlist("birad_images")
        predictions = preprocess(files)

        return jsonify(predictions), 201


class SavePrediction(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()

        if "birad_images" not in request.files:
            return "empty", 400

        files = request.files.getlist("birad_images")
        ic_no = request.form.get("ic_no")

        predictions = preprocess(files)

        # save to db
        new_prediction = Prediction(user_id=current_user, ic_no=ic_no)

        images = []
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            images.append(BIRADSImage(img_name=filename, prediction=new_prediction))

        prediction_res = []
        for item in predictions:
            for prediction in item["prediction"]:
                for img in images:
                    prediction_res.append(
                        BIRADSPrediction(
                            birads_category=prediction["birad"],
                            accuracy=prediction["accuracy"],
                            image=img,
                        )
                    )

        db.session.add_all([new_prediction, *images, *prediction_res])
        db.session.commit()

        return jsonify({"message": "Prediction stored successfully"}), 201


class ViewPrediction(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user_predictions = Prediction.query.filter_by(user_id=current_user).all()

        predictions_list = []
        for prediction in user_predictions:
            birads_predictions = BIRADSPrediction.query.filter_by(
                prediction_id=prediction.id
            ).all()
            birads_list = [
                {
                    "birads_category": bp.birads_category,
                    "accuracy": bp.accuracy,
                    "image": bp.image,
                }
                for bp in birads_predictions
            ]
            predictions_list.append(
                {
                    "prediction_id": prediction.id,
                    "input_image": prediction.input_image,
                    "result": prediction.result,
                    "created_at": prediction.created_at,
                    "birads_predictions": birads_list,
                }
            )

        return jsonify(predictions_list)
