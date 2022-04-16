from unittest import result
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash 
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app) 
from flask_app.models import bet

class User:
    schema_name = "rp_solo_schema"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.bets = []

    @classmethod
    def register_new_user(cls,data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return connectToMySQL(cls.schema_name).query_db(query,data)

    @staticmethod
    def validate_registration(form_data):
        is_valid = True
        if len(form_data["first_name"]) < 2:
            is_valid = False
            flash(" First name must be at least 2 characters.", "registration")
        if len(form_data["last_name"]) < 2:
            is_valid = False
            flash(" Last name must be at least 2 characters.", "registration")
        if not EMAIL_REGEX.match(form_data["email"]):
            is_valid = False
            flash("Email is invalid", "registration")
        data = {
            "email": form_data["email"]
        }
        found_user = User.get_by_email(data)
        if found_user != False:
            is_valid = False
            flash("Email is already registered", "registration")
        if len(form_data["password"]) < 8:
            is_valid = False
            flash("Password must be at least 8 characters", "registration")
        if form_data["password"] != form_data["confirm_pw"]:
            is_valid = False
            flash("Passwords must match", "registration")
        return is_valid

    @staticmethod
    def validate_login(form_data):
        is_valid = True
        email_data = {
            "email": form_data["email"]
        }
        found_user = User.get_by_email(email_data)
        if found_user == False:
            is_valid = False
            flash("Invalid Login Credential", "login")
            return is_valid
        if not bcrypt.check_password_hash(found_user.password, form_data["password"]):
            is_valid = False
            flash("Invalid Login Credential", "login")
        return is_valid


    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.schema_name).query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(cls.schema_name).query_db(query,data)
        if len(results) == 0:
            return None
        else:
            return cls(results[0])