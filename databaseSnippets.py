from databases import Database
import asyncio

database = Database('sqlite+aiosqlite:///snippet.db')

async def initDatabase():
    await database.connect()

    query = "DROP TABLE IF EXISTS user"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS game"
    await database.execute(query=query)

    query = """CREATE TABLE user 
                                (uID int NOT NULL PRIMARY KEY ASC, 
                                userName varchar(30) NOT NULL UNIQUE, 
                                password BLOB NOT NULL, 
                                numOfPlays int NOT NULL, 
                                numOfWins int NOT NULL, 
                                maxStreak int NOT NULL, 
                                currentStreak int NOT NULL, 
                                currentGameID int NOT NULL)
    """
    await database.execute(query=query)

    query = """CREATE TABLE game
                                (gameID NOT NULL PRIMARY KEY ASC,
                                 uID int NOT NULL,
                                 secretWord text NOT NULL,
                                 currentAttempt text NOT NULL)
    """
    await database.execute(query=query)

    query = """INSERT INTO user (uID, userName, password, numOfPlays, numOfWins, maxStreak, currentStreak, currentGameID) 
                                VALUES (:uID, :userName, :password, :numOfPlays, :numOfWins, :maxStreak, :currentStreak, :currentGameID)"""
    values = {"uID": 123, 
            "userName": "jasmineTea", 
            "password" : "attaDBS123", 
            "numOfPlays" : 1, 
            "numOfWins" : 1, 
            "maxStreak" : 1, 
            "currentStreak": 1, 
            "currentGameID": 7}
    await database.execute(query=query, values=values)

    query = """INSERT INTO game (gameID, uID, secretWord, currentAttempt) 
                                VALUES (:gameID, :uID, :secretWord, :currentAttempt)"""
    values = {"gameID": 123, 
            "uID": "jasmineTea", 
            "secretWord" : "baby", 
            "currentAttempt" : "12,13,14,15,16"}
    await database.execute(query=query, values=values)

def main():
    print("Hello World!")
    asyncio.run(initDatabase()) 

if __name__ == "__main__":
    main()