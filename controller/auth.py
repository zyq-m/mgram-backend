from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from model import User
from extensions import db, f_bcrypt


class UserLogin(Resource):
    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"message": "Email and password required"}, 400

        user = User.query.filter_by(email=email).first()

        if user and f_bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

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
        user = User.query.get(current_user)

        if user.role != "ADMIN":
            return {"message": "Admin access required"}, 403

        data = request.get_json()

        email = data.get("email")
        phone_no = data.get("phone_no")

        if not email or not phone_no:
            return {"message": "Email and phone number required"}, 400

        if (
            User.query.filter_by(email=email).first()
            or User.query.filter_by(phone_no=phone_no).first()
        ):
            return {
                "message": "User with this email or phone number already exists"
            }, 400

        new_user = User(
            email=email,
            phone_no=phone_no,
        )
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201
