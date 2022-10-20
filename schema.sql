PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS games;

CREATE TABLE user(
    userid INTEGER NOT NULL PRIMARY KEY ASC,
    username TEXT NOT NULL UNIQUE,
    pwd BLOB NOT NULL
);

CREATE TABLE games(
    username TEXT NOT NULL,
    gameid INTEGER NOT NULL PRIMARY KEY ASC,
    secretkey TEXT NOT NULL UNIQUE,
    numberOfGuesses INTEGER NOT NULL
);

-- Test user
INSERT INTO user(username, pwd)
VALUES ('username', 'password');

INSERT INTO games(username, secretkey,numberOfGuesses) VALUES('gamer1', 'flick', 0);
INSERT INTO games(username, secretkey,numberOfGuesses) VALUES('gamer2', 'texte', 0);

COMMIT;