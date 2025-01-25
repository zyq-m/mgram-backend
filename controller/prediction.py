from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import User, Prediction, BIRADSImage, BIRADSPrediction
from extensions import db


class SavePrediction(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user = get_jwt_identity()

        input_image = data.get("input_image")
        result = data.get("result")
        birads_predictions = data.get("birads_predictions")

        if not input_image or not result or not birads_predictions:
            return {
                "message": "Input image, result, and BI-RADS predictions are required"
            }, 400

        new_prediction = Prediction(
            user_id=current_user, input_image=input_image, result=result
        )
        db.session.add(new_prediction)
        db.session.commit()

        for birads_data in birads_predictions:
            birads_prediction = BIRADSPrediction(
                prediction_id=new_prediction.id,
                birads_category=birads_data["birads_category"],
                accuracy=birads_data["accuracy"],
                image=birads_data["image"],
            )
            db.session.add(birads_prediction)

        db.session.commit()

        return {"message": "Prediction stored successfully"}, 201


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
