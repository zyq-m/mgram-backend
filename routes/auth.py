from flask import Blueprint
from flask_restful import Api, reqparse, fields
from controller.auth import TokenRefresh, UserLogin, UserRegister

bp = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(bp)

api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserRegister, "/register")
