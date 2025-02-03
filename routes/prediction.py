from flask import Blueprint
from flask_restful import Api

from controller.prediction import (
    SavePrediction,
    ViewPrediction,
    PredictImage,
    ChartPrediction,
)

bp = Blueprint("predict", __name__, url_prefix="/predict")
api = Api(bp)

api.add_resource(PredictImage, "")
api.add_resource(ChartPrediction, "/chart")
api.add_resource(SavePrediction, "/save")
api.add_resource(ViewPrediction, "/<int:id>")
