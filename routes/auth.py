from flask import Blueprint
from flask_restful import Api
from controller.auth import TokenRefresh, UserLogin, UserRegister, OneUser

bp = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(bp)

api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserRegister, "/user")
api.add_resource(OneUser, "/user/<int:id>")
