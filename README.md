# CPSC 449 - Project 1 - Wordle Mock Backend

This is the main repository for the Wordle Mock Backend App. This README describes how to run the app and test the various access points.

#### Authors
Section 02
Group 20
Members: 
- Divyansh Mohan Rao (divyanshrao@csu.fullerton.edu)
- Ken Cue (kencue@csu.fullerton.edu)
- Sam Le (hle406@csu.fullerton.edu)
- Sam Truong (samtruonh@csu.fullerton.edu)


## Setup
### Requirements
- Python 3 (with pip)
- Quart
- SQLite 3
- Databases
- SQLAlchemy (==v1.4.41) *see [Known Issues](#known-issues) section*
- Foreman
- Quart-Schema
- HTTPie
- PyTest

Run the following commands if any of the required libraries are missing:
```
$ sudo snap install httpie
$ sudo apt update
$ sudo apt install --yes python3-pip ruby-foreman sqlite3

$ python3 -m pip install --upgrade quart[dotenv] click markupsafe Jinja2
$ python3 -m pip install sqlalchemy==1.4.41
$ python3 -m pip install databases[aiosqlite]
$ python3 -m pip install quart-schema
```

### Initializing the Database
Before running the app, run the following command to initialize the database and populate the tables for the correct and valid words.
```
$ ./init.sh
```

### Launching the App
Use the following command to start the app. Take note of the URI of the app in the output.
```
$ foreman start
```


## Running the App
The HTTPie commands listed in this section run under the assumption that the default localhost URI `127.0.0.1` is used and that the port value of `3000` in `.env` has not been changed. 

### User Authentication Routes
##### Logging In
```
http POST http://127.0.0.1:3000/login --auth <username>:<password>
```

##### Register using httpie
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

## Testing
```
pytest test_api.py
```

## Known Issues

- There seems to be an issue with SQLAlchemy v1.4.42 that breaks Databases. Downgrading to v1.4.41 seems to remove this issue as mentioned in [this StackOverflow entry](https://stackoverflow.com/questions/74089620/python-databases-library-cant-fetch-all-from-mysql-database).