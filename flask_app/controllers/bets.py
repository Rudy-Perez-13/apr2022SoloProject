from crypt import methods
from flask_app.models import user, bet
from flask import request, render_template, redirect, session, flash, url_for
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app) 
from flask_app.controllers import users


@app.route('/new/bet')
def add_new():
    if "user_id" not in session:
        return redirect('/')
    data = {
        "id": session["user_id"]
    }
    return render_template("new_bet.html", user = user.User.get_by_id(data))

@app.route('/show/<int:id>')
def view_bet(id):
    if "user_id" not in session:
        return redirect('/')
    data = {
        "id": id,
    }
    user_data = {
        "id": session["user_id"]
    }
    return render_template("view_bet.html", one_bet = bet.Bet.grab_one_bet(data), user = user.User.get_by_id(user_data))

@app.route('/edit/<int:id>')
def edit_bet(id):
    if "user_id" not in session:
        return redirect('/')
    data = {
        "id": id,
    }
    user_data = {
        "id": session["user_id"]
    }
    return render_template("edit_bet.html", one_bet = bet.Bet.grab_one_bet(data), user = user.User.get_by_id(user_data))

@app.route('/create_bet', methods=["POST"])
def add_bet_to_db():
    if "user_id" not in session:
        return redirect('/')
    if not bet.Bet.validate_form(request.form):
        return redirect('/new/bet')
    data = {
        "bet": request.form["bet"],
        "odds": request.form["odds"],
        "wager": request.form["wager"],
        "result": request.form["result"],
        "user_id": session["user_id"],
    }
    bet.Bet.add_bet(data)
    return redirect("/dashboard")

@app.route('/update_bet/<int:id>', methods=["POST"])
def update_bet(id):
    if "user_id" not in session:
        return redirect('/')
    if not bet.Bet.validate_form(request.form):
        return redirect(url_for('edit_bet', id=id))
    data = {
        "bet": request.form["bet"],
        "odds": request.form["odds"],
        "wager": request.form["wager"],
        "result": request.form["result"],
        "id": id,
    }
    bet.Bet.edit_bet(data)
    return redirect("/dashboard")

@app.route('/delete/<int:id>')
def delete_bet(id):
    data = {
        "id": id,
    }
    bet.Bet.delete_bet(data)
    return redirect("/dashboard")

@app.route('/bets/like/<int:id>')
def like_bet(id):
    if "user_id" not in session:
        return redirect('/')
    data = {
        "user_id": session["user_id"],
        "bet_id": id,
    }
    bet.Bet.like_bet(data)
    return redirect("/dashboard")
