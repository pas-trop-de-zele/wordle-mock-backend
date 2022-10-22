# Project 1 - Wordle Mock Backend

import toml
import sqlite3
import databases
import base64

from typing import Tuple
from quart import Quart, jsonify, g, request, abort

app = Quart(__name__)  

app.config.from_file(f"./config/{__name__}.toml", toml.load)


async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()


# ----------------------------Routes---------------------------- #

@app.route("/", methods=["GET"])
async def home():
    return jsonify_message("Welcome to wordle!")


@app.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "GET":
        return jsonify_message("Send based64(username:password) in Authorization header")
    else:
        username, password = get_username_password_from_header(request)
        db = await _get_db()
        query = "SELECT username, pwd FROM user WHERE username = :username AND pwd = :pwd"
        user = await db.fetch_one(query=query, values={"username": username, "pwd": password})
        if not user:
            return jsonify_message("Invalid/ Missing username or password. Send based64(username:password) in Authorization header"), 401, {"WWW-Authenticate": "Basic"}
        return {"authenticated": True}, 200


@app.route("/register", methods=["GET", "POST"])
async def register():
    if request.method == "GET":
        return jsonify_message("Pass in username and password in POST request")
    else:
        data = await request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify_message("Required username and password"), 400
        is_user = await is_user_exists(data['username'])
        if is_user :
            return jsonify_message("Username not availabe"), 400

        await insert_user(data["username"], data["password"])
        return jsonify_message("User registered")


async def is_user_exists(username) -> bool:
    db =  await _get_db()
    query = "SELECT username FROM user WHERE username = :username"
    user = await db.fetch_all(query=query, values={"username": username})
    return True if user and len(user) > 0 else False


async def insert_user(username, password) -> None:
    db = await _get_db()
    query = "INSERT INTO user(username, pwd) VALUES(:username, :pwd)"
    values = {"username": username, "pwd": password}
    await db.execute(query=query, values=values)


def get_username_password_from_header(req) -> Tuple[str, str]:
    if "Authorization" not in request.headers:
        return "",""
    hashBytes = req.headers["Authorization"].split()[1]
    username, passsword = base64.b64decode(hashBytes).decode("utf-8").split(":")
    return username, passsword


@app.route("/wordle/start", methods=["GET", "POST"])
async def start_game():
    if request.method == "GET":
        return jsonify_message("Pass in username to start the game")
    else:
        data = await request.get_json()

        if not data or 'username' not in data:
            return jsonify_message("Required username"), 400

        db =  await _get_db()
        query = "SELECT userid FROM user WHERE username = :username"
        user = await db.fetch_one(query=query, values={"username": data['username']})
        userid = 0
        if not user:
            return jsonify_message("Username not Found, Please register " + data['username']), 404
        else:
            userid = user["userid"]

        secret_word = generate_secret_word()
        try:
            query = "INSERT INTO games(userid, secretWord) VALUES(:userid, :secret_word)"
            values = {"userid": userid, "secret_word": secret_word}
            cursor = await db.execute(query=query, values=values)
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return jsonify_message(f"game started with id: {cursor.lastrowid}")


async def generate_secret_word() -> str:
    db =  await _get_db()
    query = "SELECT * FROM secret_word ORDER BY RANDOM() LIMIT 1;"
    secret_word = await db.fetch_one(query=query)
    return secret_word["word"]


@app.route("/wordle/<string:username>/games", methods=["GET"])
async def list_active_games(username):
    db =  await _get_db()
    query = """
            SELECT gameid 
            FROM games
            LEFT JOIN user ON games.userid = user.userid
            WHERE username = :username AND isActive = 1
            """
    games = await db.fetch_all(query=query, values={"username": username})

    # print("game",game)
    if games:
        return list(map(dict, games))
    else:
        abort(404)


@app.route("/wordle/<string:username>/<int:gameid>/status", methods=["GET"])
async def retrieve_game(username, gameid):
    db =  await _get_db()
    query = """
            SELECT guess, secretWord as secret_word
            FROM guesses
            LEFT JOIN games ON guesses.gameid = games.gameid
            LEFT JOIN user ON games.userid = user.userid
            WHERE username = :username AND games.gameid = :gameid AND isActive = 1
            """
    guesses = await db.fetch_all(query=query, values={"username": username, "gameid": gameid})
    num_guesses = len(guesses)
    list_guesses = []
    for guess in guesses:
        correct_letters, correct_indices = compare_guess(guess.guess, guess.secret_word)
        list_guesses.append({
            "guess": guess.guess,
            "correct_letters": correct_letters,
            "correct_indices": correct_indices
        })
    if guesses:
        return {
            "num_guesses": num_guesses,
            "guesses": list_guesses
        }
    else:
        abort(404)


@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409



# ----------------------------Helpers---------------------------- #

def jsonify_message(message):
    return {"message": message}


def compare_guess(guess, secret_word):
    correct_letters = set()
    correct_indices = []
    for sw_idx in range(0, len(secret_word)):
        for g_idx in range(0, len(guess)):
            if sw_idx == g_idx and guess[g_idx] == secret_word[sw_idx]:
                correct_indices.append(g_idx)
            if guess[g_idx] == secret_word[sw_idx]:
                correct_letters.add(guess[g_idx])
    return list(correct_letters), correct_indices


def check_guess(guess, secret_word):
    correct_letters, correct_indices = compare_guess(guess, secret_word)
    if len(secret_word) == len(correct_indices):
        is_correct = True
    else:
        is_correct = False
    return is_correct
