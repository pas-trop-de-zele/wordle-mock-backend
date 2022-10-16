PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS user;

CREATE TABLE user(
    userid INTEGER NOT NULL PRIMARY KEY ASC,
    username TEXT NOT NULL UNIQUE,
    pwd BLOB NOT NULL
);

-- Test user
INSERT INTO user(username, pwd)
VALUES ('username', 'password');

COMMIT;