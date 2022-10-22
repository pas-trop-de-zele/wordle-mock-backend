# wordle-mock-backend

## Setup
### Requirements
    - Python 3 (with pip)
    - Quart
    - SQLite 3
    - Databases
    - SQLAlchemy (==v1.4.41) __see Known Issues__
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



## Testing

```
pytest test_api.py
```

## Running the App

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



## Known Issues

- There seems to be an issue with SQLAlchemy v1.4.42 that breaks Databases. Downgrading to v1.4.41 seems to remove this issue as mentioned in [this StackOverflow entry](https://stackoverflow.com/questions/74089620/python-databases-library-cant-fetch-all-from-mysql-database).