# wordle-mock-backend

## Setup
### Requirements
Python 3 (+ pip), Quart, SQLite 3, Foreman, PyTest, HTTPie

```
$ sudo snap install httpie
$ sudo apt update
$ sudo apt install --yes python3-pip ruby-foreman sqlite3

$ python3 -m pip install --upgrade quart[dotenv] click markupsafe Jinja2
$ python3 -m pip install databases[aiosqlite]
$ python3 -m pip install quart-schema
```


## Testing

```
pytest test_api.py
```

## Running the App

#### How to launch app
```
$ foreman start
```

#### Login using httpie
```
http POST <insert local url here>/login --auth <username>:<password>
```

#### Register using httpie
```
http POST <insert local url here>/register username=<new username> password=<new password>
```

#### Start a game using httpie
```
http  <insert local url here>/startgame username=<new username>
```

#### list all the games using httpie
```
http  <insert local url here>/listAllGames/<string:username>
```

#### retrive a games using httpie
```
http  <insert local url here>/retrievegame/<int:gameid>
```
