from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from model import User
from extensions import db, f_bcrypt

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name are required", required=True)
parser.add_argument("email", type=str, help="Email are required", required=True)
parser.add_argument("phone", type=str, help="Phone are required", required=True)

user_fields = {
    "id": fields.String,
    "email": fields.String,
    "name": fields.String,
    "phone": fields.String(attribute="phone_no"),
}


class UserLogin(Resource):
    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"message": "Email and password required"}, 400

        user = User.query.filter_by(email=email).first()
        identity = {
            "id": user.id,
            "role": user.role,
            "email": user.email,
            "name": user.name,
        }

        if user and f_bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": user.email,
                    "role": user.role,
                    "phone_no": user.phone_no,
                },
            }, 200

        return {"message": "Invalid credentials"}, 401


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {"access_token": access_token}, 200


class UserRegister(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user["id"]).first()

        if user.role != "ADMIN":
            return {"message": "Admin access required"}, 403

        args = parser.parse_args()

        if (
            User.query.filter_by(email=args["email"]).first()
            or User.query.filter_by(phone_no=["phone"]).first()
        ):
            return {
                "message": "User with this email or phone number already exists"
            }, 400

        new_user = User(
            email=args["email"],
            name=args["name"],
            phone_no=args["phone"],
        )
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201

    @jwt_required()
    @marshal_with(user_fields)
    def get(self):
        return User.query.filter_by(role="USER").all()


class OneUser(Resource):
    @jwt_required()
    def put(self, id):
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(id=current_user["id"]).first()

        if current_user.role != "ADMIN":
            return {"message": "Admin access required"}, 403

        args = parser.parse_args()

        user = User.query.filter_by(id=id).first_or_404()
        user.email = args["email"]
        user.phone_no = args["phone"]
        user.name = args["name"]

        db.session.commit()

        return {"message": "User updated successfully"}, 200

    @jwt_required()
    @marshal_with(user_fields)
    def get(self, id):
        user = User.query.filter_by(id=id).first_or_404()
        return user, 200
