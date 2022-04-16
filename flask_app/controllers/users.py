from flask_app.models import user, bet
from flask import request, render_template, redirect, session, flash
from flask_app import app
from flask_app.models import bet
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app) 
from flask_app.controllers import bets


@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect('/')
    data = {
        "id": session["user_id"]
    }
    return render_template("dashboard.html", user = user.User.get_by_id(data), all_bets = bet.Bet.grab_bets_with_user(data), all_liked_won_bets = bet.Bet.grab_all_won_bets_with_likes(data))

@app.route('/register', methods=["POST"])
def register_new_user():
    if not user.User.validate_registration(request.form):
        return redirect('/')
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": bcrypt.generate_password_hash(request.form["password"])
    }
    session["user_id"] = user.User.register_new_user(data)
    return redirect("/dashboard")


@app.route('/login', methods=["POST"])
def login_user():
    if not user.User.validate_login(request.form):
        return redirect('/')
    data = {
        "email": request.form["email"]
    }
    logged_in_user = user.User.get_by_email(data)
    session["user_id"] = logged_in_user.id
    return redirect("/dashboard")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
