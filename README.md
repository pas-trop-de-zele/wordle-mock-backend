# wordle-mock-backend

## Testing

```
pytest test_api.py
```

## How to launch app

```
$ foreman start
```

## Login using httpie

```
http POST <insert local url here>/login --auth <username>:<password>
```

## Register using httpie

```
http POST <insert local url here>/register username=<new username> password=<new password>
```

## Start a game using httpie

```
http  <insert local url here>/startgame username=<new username>
```

## list all the games using httpie

```
http  <insert local url here>/listAllGames/<string:username>
```

## retrive a games using httpie

```
http  <insert local url here>/retrievegame/<int:gameid>
```

## databases implementation


The database is implemented via. the Databases library. The database has to be initiated in an async function using databases library.

In the databasesSnippets.py are examples of how to execute SQL calls through the databases library.

Tables are already initialized in the init function and it can be copied into the app.py to be used.

To execute one single insert SQL query through the databases library: 


```
query = """INSERT INTO user (uID, userName, password, currentGameID) 
                                VALUES (:uID, :userName, :password, :currentGameID)"""
values = {"uID": 123, 
            "userName": "jasmineTea", 
            "password" : "attaDBS123", 
            "currentGameID": 7}
await database.execute(query=query, values=values)
```

To execute many insert SQL queries through the databases library:


```
query = """INSERT INTO guessesMade (gameID, guess) 
                                VALUES (:gameID, :guess)"""
values = [
    {"gameID": "123", "guess": "flower"},
    {"gameID": "123", "guess": "cupcake"}]
await database.execute_many(query=query, values=values)
```

You can query SQL statements too:

# Fetch multiple rows

```
query = "SELECT * FROM notes WHERE completed = :completed"
rows = await database.fetch_all(query=query, values={"completed": True})
```

# Fetch single row

```
query = "SELECT * FROM notes WHERE id = :id"
result = await database.fetch_one(query=query, values={"id": 1})
```

Summary source: https://www.encode.io/databases/database_queries/ 


