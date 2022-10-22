# Initialize database and populate initial values

from databases import Database

import asyncio
import json

database = Database('sqlite+aiosqlite:///wordle_app.db')

async def init_db():
    await database.connect()

    query = "DROP TABLE IF EXISTS user"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS games"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS guesses"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS secret_word"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS valid_words"
    await database.execute(query=query)
    

    query = """
            CREATE TABLE user (
                userid INTEGER NOT NULL PRIMARY KEY ASC, 
                username TEXT NOT NULL UNIQUE, 
                pwd BLOB NOT NULL,
                dateCreated TEXT
            )
            """
    await database.execute(query=query)

    query = """ 
            CREATE TABLE games (
                gameid INTEGER NOT NULL PRIMARY KEY ASC,
                userid INTEGER NOT NULL,
                secretWord TEXT NOT NULL,
                isActive INTEGER DEFAULT 0 NOT NULL,
                hasWon INTEGER DEFAULT 0 NOT NULL,
                dateCreated TEXT
            )
            """
    await database.execute(query=query)

    query = """
            CREATE TABLE guesses (
                guessid INTEGER NOT NULL PRIMARY KEY ASC,
                gameid INTEGER NOT NULL,
                guess TEXT NOT NULL,
                dateCreated TEXT
            )
            """
    await database.execute(query=query)

    query = """ 
            CREATE TABLE secret_word (
                word TEXT PRIMARY KEY
            )
            """
    await database.execute(query=query)

    query = """ 
            CREATE TABLE valid_words (
                word TEXT PRIMARY KEY
            )
            """
    await database.execute(query=query)


async def populate_tables():
    # fill secret_word and valid_words with words from correct.json and valid.json respectively
    correct_json = open("share/correct.json")
    valid_json = open("share/valid.json")
    
    print("Populating secret_word table...")
    query = """
            INSERT INTO secret_word (word) VALUES (:word)
            """
    values = []
    data = json.load(correct_json)
    for word in data:
        values.append({"word": word})
    await database.execute_many(query=query, values=values)

    print("Populating valid_words table...")
    query = """
            INSERT INTO valid_words (word) VALUES (:word)
            """
    values = []
    data = json.load(valid_json)
    for word in data:
        values.append({"word": word})
    await database.execute_many(query=query, values=values)


def main():
    asyncio.run(init_db()) 
    asyncio.run(populate_tables())

if __name__ == "__main__":
    main()