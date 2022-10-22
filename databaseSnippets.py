from databases import Database
import asyncio

database = Database('sqlite+aiosqlite:///schema.db')

async def initDatabase():
    await database.connect()

    query = "DROP TABLE IF EXISTS user"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS game"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS guessesMade"
    await database.execute(query=query)


    query = """CREATE TABLE user 
                                (uID int NOT NULL PRIMARY KEY ASC, 
                                userName varchar(30) NOT NULL UNIQUE, 
                                password BLOB NOT NULL, 
                                currentGameID int NOT NULL)
    """
    await database.execute(query=query)

    query = """CREATE TABLE game
                                (gameID NOT NULL PRIMARY KEY ASC,
                                 uID int NOT NULL,
                                 secretWord text NOT NULL)
    """
    await database.execute(query=query)

    query = """CREATE TABLE guessesMade
                                (gameID NOT NULL,
                                 guess text NOT NULL)
    """
    await database.execute(query=query)


async def exampleOperations():
    query = """INSERT INTO user (uID, userName, password, currentGameID) 
                                VALUES (:uID, :userName, :password, :currentGameID)"""
    values = {"uID": 123, 
            "userName": "jasmineTea", 
            "password" : "attaDBS123", 
            "currentGameID": 7}
    await database.execute(query=query, values=values)

    query = """INSERT INTO game (gameID, uID, secretWord) 
                                VALUES (:gameID, :uID, :secretWord)"""
    values = {"gameID": 123, 
            "uID": "jasmineTea", 
            "secretWord" : "baby"}
    await database.execute(query=query, values=values)

    query = """INSERT INTO guessesMade (gameID, guess) 
                                VALUES (:gameID, :guess)"""
    values = [
    {"gameID": "123", "guess": "flower"},
    {"gameID": "123", "guess": "cupcake"}]
    await database.execute_many(query=query, values=values)

def main():
    asyncio.run(initDatabase()) 
    asyncio.run(exampleOperations())

if __name__ == "__main__":
    main()