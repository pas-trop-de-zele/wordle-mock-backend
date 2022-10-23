# Project 1 - Wordle Mock Backend

import toml
import sqlite3
import databases
import base64
import dataclasses

from typing import Tuple, Optional
from quart import Quart, jsonify, g, request, abort
from quart_schema import QuartSchema, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./config/{__name__}.toml", toml.load)


@dataclasses.dataclass
class Guess:
    guess: str


@dataclasses.dataclass
class Username:
    username: str


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
    """
    Home
    
    This is just the welcome message.
    """
    
    return jsonify_message("Welcome to wordle!")


@app.route("/login", methods=["GET", "POST"])
async def login():
    """
    Login
    
    Authenticate user from username & password pass through the header.
    """

    if request.method == "GET":
        return jsonify_message("Send as POST with based64(username:password) in Authorization header")
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
    """
    Register
    
    Register a user. 
    Note: Use HTTPie to test this route (not /docs or /redocs). See README.md for more info.
    """

    if request.method == "GET":
        return jsonify_message("Pass in username and password in POST request")
    else:
        data = await request.get_json()
        db =  await _get_db()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify_message("Required username and password"), 400
        is_user = await is_user_exists(db, data['username'])
        if is_user :
            return jsonify_message("Username not availabe"), 400

        await insert_user(db, data["username"], data["password"])
        return jsonify_message("User registered")


async def is_user_exists(db, username) -> bool:
    query = "SELECT username FROM user WHERE username = :username"
    user = await db.fetch_all(query=query, values={"username": username})
    return True if user and len(user) > 0 else False


async def insert_user(db, username, password) -> None:
    query = "INSERT INTO user(username, pwd) VALUES(:username, :pwd)"
    values = {"username": username, "pwd": password}
    await db.execute(query=query, values=values)


def get_username_password_from_header(req) -> Tuple[str, str]:
    if "Authorization" not in request.headers:
        return "",""
    hashBytes = req.headers["Authorization"].split()[1]
    username, passsword = base64.b64decode(hashBytes).decode("utf-8").split(":")
    return username, passsword


@app.route("/wordle/start", methods=["POST"])
@validate_request(Username)
async def start_game(data: Username):
    """
    Start Game
    
    Initializes a game. Returns the game ID if successful.
    """

    data = await request.get_json()

    if not data or 'username' not in data:
        return jsonify_message("Required username"), 400

    db =  await _get_db()
    query = "SELECT userid FROM user WHERE username = :username"
    user = await db.fetch_one(query=query, values={"username": data['username']})
    userid = 0
    if not user:
        return jsonify_message(f"Username not Found, Please register {data['username']}"), 404
    else:
        userid = user["userid"]

    query = "SELECT * FROM secret_word ORDER BY RANDOM() LIMIT 1"
    secret_word = await db.fetch_one(query=query)

    try:
        query = "INSERT INTO games(userid, secretWord) VALUES(:userid, :secret_word)"
        values = {"userid": userid, "secret_word": secret_word.word}
        last_insert_id = await db.execute(query=query, values=values)
    except sqlite3.IntegrityError as e:
        abort(409, e)
    return jsonify_message(f"Game started with id: {last_insert_id}.")


@app.route("/wordle/<string:username>/games", methods=["GET"])
async def list_active_games(username):
    """
    List Active Games
    
    This generates a list of game IDs that are active. Games that ran out of attempts 
    or games that have been won are not included in the list.
    """

    db =  await _get_db()
    query = """
            SELECT gameid 
            FROM games
            LEFT JOIN user ON games.userid = user.userid
            WHERE username = :username AND isActive = 1
            """
    games = await db.fetch_all(query=query, values={"username": username})

    if games:
        return list(map(dict, games))
    else:
        return jsonify_message(f"No active games found for user, {username}."), 404


async def is_active_game(db, username, gameid) -> bool:
    query = """
            SELECT *
            FROM games
            LEFT JOIN user ON games.userid = user.userid
            WHERE username = :username AND games.gameid = :gameid AND isActive = 1
            """
    game = await db.fetch_one(query=query, values={"username": username, "gameid": gameid})
    if game:
        return True
    else:
        return False
        

@app.route("/wordle/<string:username>/<int:gameid>/status", methods=["GET"])
async def retrieve_game(username, gameid):
    """
    Retrieve Game
    
    This displays the current state of a specified active game. It lists all the attempts, as well as,
    the details of how close the attempts are from the secret word. This also shows the number
    of attempts left before the game ends.
    """

    db =  await _get_db()

    if await is_active_game(db, username, gameid):
        query = """
                SELECT guess, secretWord as secret_word
                FROM guesses
                LEFT JOIN games ON guesses.gameid = games.gameid
                WHERE games.gameid = :gameid AND isActive = 1
                """
        guesses = await db.fetch_all(query=query, values={"gameid": gameid})

        return calculate_game_status(guesses)
    else:
        abort(404)


def calculate_game_status(guesses):
    # clean up and check guesses
    num_guesses = len(guesses)
    list_guesses = []
    for guess in guesses:
        correct_letters, correct_indices = compare_guess(guess.guess, guess.secret_word)
        list_guesses.append({
            "guess": guess.guess,
            "correct_letters": correct_letters,
            "correct_indices": correct_indices
        })

    return {
        "num_guesses": num_guesses,
        "max_attempts": app.config["WORDLE"]["MAX_NUM_ATTEMPTS"],
        "guesses": list_guesses
    }


@app.route("/wordle/<string:username>/<int:gameid>/guess", methods=["POST"])
@validate_request(Guess)
async def make_guess(username, gameid, data: Guess):
    """
    Guess the Secret Word
    
    This inserts a guess into the guesses table if the guess word is a valid word. If the
    guess is valid, it will show whether it is correct and display hints accordingly. It
    will also tell the player how many attempts they have left.
    """

    data = await request.get_json()
    db =  await _get_db()

    if await is_active_game(db, username, gameid):
        # validate the guessed word first
        if len(data["guess"]) != app.config["WORDLE"]["WORDLE_LENGTH"]:
            return jsonify_message(f"Not a valid guess! Please only guess {app.config['WORDLE']['WORDLE_LENGTH']}-letter words. This attempt does not count.")
        else:
            query = "SELECT * FROM valid_words WHERE word = :guess"
            is_valid = await db.fetch_one(query=query, values={"guess": data["guess"]})

            if not is_valid:
                return jsonify_message(f"{data['guess']} is not a valid word! Try again. This attempt does not count.")

        # guess was valid, proceed to store and check game state
        try:
            query = """
                    INSERT INTO guesses(gameid, guess) VALUES(:gameid, :guess)
                    """
            await db.execute(query=query, values={"gameid": gameid, "guess": data["guess"]})
        except sqlite3.IntegrityError as e:
            # guesses are unique per game
            abort(409, e)
        
        # grab the secret word
        query = """
                SELECT secretWord AS secret_word FROM games WHERE gameid = :gameid
                """
        game = await db.fetch_one(query=query, values={"gameid": gameid})
        secret_word = game.secret_word 


        query = """
                SELECT guess, secretWord as secret_word
                FROM guesses
                LEFT JOIN games ON guesses.gameid = games.gameid
                WHERE games.gameid = :gameid AND isActive = 1
                """
        guesses = await db.fetch_all(query=query, values={"gameid": gameid})
        guesses = calculate_game_status(guesses)

        is_correct = check_guess(data["guess"], secret_word)
        max_num_attempts = app.config["WORDLE"]["MAX_NUM_ATTEMPTS"]

        if is_correct:
            query = """
                    UPDATE games 
                    SET isActive = 0, hasWon = 1
                    WHERE gameid = :gameid
                    """
            await db.execute(query=query, values={"gameid": gameid})

            return jsonify_message(f"Correct! The answer was {secret_word}.")
        elif guesses["num_guesses"] == max_num_attempts and not is_correct:
            query = """
                    UPDATE games 
                    SET isActive = 0
                    WHERE gameid = :gameid
                    """
            await db.execute(query=query, values={"gameid": gameid})
            
            return jsonify_message(f"You have lost! You have made {max_num_attempts} incorrect attempts. The secret word was {secret_word}.")
        else:
            remaining_attempts = max_num_attempts - guesses["num_guesses"]
            return {
                "message": f"Try again! You have {remaining_attempts} more attampts left.",
                "guesses": guesses
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
