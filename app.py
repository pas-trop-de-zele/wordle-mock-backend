from typing import Tuple
from uuid import UUID
from quart import g, Quart, jsonify, request, abort
import sqlite3
import base64
import json
import random

# ----------------------------Setting up----------------------------
app = Quart(__name__)  
app.config.update({
  "DATABASE": app.root_path / "schema.db",
})

def _connect_db():
    engine = sqlite3.connect(app.config["DATABASE"]) 
    engine.row_factory = sqlite3.Row
    return engine

def init_db():
    db = _connect_db()
    with open(app.root_path / "schema.sql", mode="r") as file_:
        db.cursor().executescript(file_.read())
    db.commit()

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

init_db()

# ----------------------------Routes----------------------------
@app.route("/", methods=["GET"])
async def home():
    return "Welcome to wordle!"

@app.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "GET":
        return "Send based64(username:password) in Authorization header"
    else:
        username, password = getUsernamePasswordFromHeader(request)
        db = get_db()
        cur = db.execute(
            "SELECT username, pwd FROM user WHERE username = ? AND pwd = ?", (username, password)
        )
        user = cur.fetchall()
        if not user:
            return "Invalid username or password", 401, {"WWW-Authenticate": "Basic"}
        return {"authenticated": True}, 200

@app.route("/register", methods=["GET", "POST"])
async def register():
    if request.method == "GET":
        return "Pass in username and password in POST request"
    else:
        data = await request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return "Required username and password", 400
        isUser = await isUserExisted(data['username'])
        if isUser :
            return "Username not availabe", 400

        await insertUser(data["username"], data["password"])
        return "User registered"

async def isUserExisted(username) -> bool:
    db =  get_db()
    cur = db.execute(
        "SELECT username FROM user WHERE username = ?", (username,)
    )
    user = cur.fetchall()
    return True if user and len(user) > 0 else False

async def insertUser(username, password) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO user(username, pwd) VALUES(?, ?)", (username, password,)
    )
    db.commit()
        
def getUsernamePasswordFromHeader(req) -> Tuple[str, str]:
    if "Authorization" not in request.headers:
        return "",""
    hashBytes = req.headers["Authorization"].split()[1]
    username, passsword = base64.b64decode(hashBytes).decode("utf-8").split(":")
    return username, passsword


@app.route("/startgame", methods=["GET", "POST"])
async def startGame ():
    if request.method == "GET":
        return "Pass in username to start the game"
    else:
        data = await request.get_json()
        if not data or 'username' not in data:
            return "Required username", 400
        isUser = await isUserExisted(data['username'])
        if not isUser:
            return "Username not Found, Please register " + data['username'], 404
        db =  get_db()
        cur = db.execute(
            "SELECT username FROM games WHERE username = ?", (data["username"],)
        )
        user = cur.fetchall()
        if user:
            return "Game Exists"
        f = open('correct.json')
        jsonData = json.load(f)
        try:
            id =  db.execute(
            "INSERT INTO games(username, secretkey,numberOfGuesses) VALUES(?, ?, ?)", (data["username"], random.choice(jsonData),0,)
            )
            db.commit()
        except sqlite3.IntegrityError as e:
            abort(409, e)
        return f'game started with id: {id.lastrowid}' 

@app.route("/listallgames/<string:username>", methods=["GET"])
def listAllGame (username):
    db =  get_db()
    game =  db.execute(
            "SELECT gameId,numberOfGuesses, username FROM games WHERE username = ?", (username,)
        )

    game = game.fetchall()
    print("game",game)
    if game:
        return list(map(dict, game))
    else:
        abort(404)

@app.route("/retrievegame/<int:gameid>", methods=["GET"])
def retrieveGame (gameid):
    db =  get_db()
    game =  db.execute(
            "SELECT gameId,numberOfGuesses, username FROM games WHERE gameid = ?", (gameid,)
        )

    game = game.fetchall()
    print("game",game)
    if game:
        return list(map(dict, game))
    else:
        abort(404)