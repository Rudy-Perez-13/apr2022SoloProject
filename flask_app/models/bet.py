from mimetypes import init
from unittest import result
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash 
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)  
from flask_app.models import user

class Bet:
    schema_name = "rp_solo_schema"

    def __init__(self, data):
        self.id = data["id"]
        self.bet = data["bet"]
        self.odds = data["odds"]
        self.wager = data["wager"]
        self.result = data["result"]
        self.user_id = data["user_id"]
        self.user = None
        self.like_count = 0
        self.is_liked_by_logged_in_user = False

    @classmethod
    def add_bet(cls,data):
        query = "INSERT INTO bets (bet, odds, wager, result, user_id) VALUES (%(bet)s,%(odds)s, %(wager)s,%(result)s,%(user_id)s);"
        return connectToMySQL(cls.schema_name).query_db(query,data)

    @classmethod
    def edit_bet(cls,data):
        query = "UPDATE bets SET bet = %(bet)s, odds = %(odds)s,wager = %(wager)s,result = %(result)s WHERE id = %(id)s;"
        return connectToMySQL(cls.schema_name).query_db(query,data)

    @classmethod
    def grab_bets_with_user(cls,data):
        query = "SELECT * FROM bets WHERE bets.user_id = %(id)s;"
        return connectToMySQL(cls.schema_name).query_db(query,data)


    @classmethod
    def grab_all_won_bets(cls):
        query = "SELECT * FROM bets JOIN users ON bets.user_id = users.id WHERE result='won';"
        return connectToMySQL(cls.schema_name).query_db(query)

    @classmethod
    def grab_one_bet(cls,data):
        query = "SELECT * FROM bets JOIN users ON bets.user_id = users.id WHERE bets.id =%(id)s;"
        results = connectToMySQL(cls.schema_name).query_db(query,data)
        if len(results) == 0:
            return None
        else:
            this_bet = cls(results[0])
            user_data = {
                "id": results[0]['users.id'],
                "first_name": results[0]['first_name'],
                "last_name": results[0]['last_name'],
                "email": results[0]['email'],
                "password": results[0]['password'],
                "created_at": results[0]['users.created_at'],
                "updated_at": results[0]['users.updated_at'],
            }
            this_user = user.User(user_data)
            this_bet.user = this_user
        return this_bet

    @classmethod
    def delete_bet(cls,data):
        query = "DELETE FROM bets WHERE id = %(id)s;"
        return connectToMySQL(cls.schema_name).query_db(query,data)

    @staticmethod
    def validate_form(bet_data):
        is_valid = True
        if len(bet_data["bet"]) < 5:
            is_valid = False
            flash(" Bet must be at least 5 characters.")
        return is_valid

    @classmethod
    def like_bet(cls, data):
        query = "INSERT INTO liked_bets (user_id, bet_id) VALUES (%(user_id)s, %(bet_id)s);"
        return connectToMySQL(cls.schema_name).query_db(query,data)

    """SELECT * FROM bets JOIN users ON users.id = bets.user_id
LEFT JOIN (SELECT bet_id, COUNT(bet_id) AS bet_count FROM liked_bets GROUP BY bet_id) bet_counts
ON bets.id = bet_counts.bet_id
LEFT JOIN (SELECT bet_id FROM liked_bets WHERE user_id = 3) bet_liked_by_user
ON bets.id = bet_liked_by_user.bet_id
WHERE result='won';"""

    @classmethod
    def grab_all_won_bets_with_likes(cls,data):
        query = """SELECT * FROM bets JOIN users ON users.id = bets.user_id
                LEFT JOIN (SELECT bet_id, COUNT(bet_id) AS bet_count FROM liked_bets GROUP BY bet_id) bet_counts
                ON bets.id = bet_counts.bet_id
                LEFT JOIN (SELECT bet_id FROM liked_bets WHERE user_id = %(id)s) bet_liked_by_user
                ON bets.id = bet_liked_by_user.bet_id
                WHERE result='won';"""
        results = connectToMySQL(cls.schema_name).query_db(query,data)
        if len(results) == 0:
            return []
        else:
            bet_instances = []
            for this_bet_dictionary in results:
                bet_instance = cls(this_bet_dictionary)

                this_user_dictionary = {
                    "id": this_bet_dictionary['users.id'],
                    "first_name": this_bet_dictionary['first_name'],
                    "last_name": this_bet_dictionary['last_name'],
                    "password": this_bet_dictionary['password'],
                    "email": this_bet_dictionary['email'],
                    "created_at": this_bet_dictionary['users.created_at'],
                    "updated_at": this_bet_dictionary['users.updated_at'],
                }
                this_user_instance = user.User(this_user_dictionary)
                bet_instance.user = this_user_instance
                if this_bet_dictionary['bet_count'] != None:
                    bet_instance.like_count = this_bet_dictionary['bet_count']
                if this_bet_dictionary['bet_liked_by_user.bet_id'] != None:
                    bet_instance.is_liked_by_logged_in_user = True
                bet_instances.append(bet_instance)
        return bet_instances
