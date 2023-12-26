-- words table
CREATE TABLE WORDS (
    id INTEGER PRIMARY KEY ,
    word TEXT NOT NULL,
    game_count INTEGER NOT NULL,
    success_count INTEGER NOT NULL
);

-- games table
CREATE TABLE GAMES (
    id INTEGER PRIMARY KEY ,
    date TEXT NOT NULL,
    word_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES WORDS(id),
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);

-- users table
CREATE TABLE USERS (
    id INTEGER PRIMARY KEY ,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    nationality TEXT NOT NULL,
    played_games INTEGER NOT NULL,
    games_won INTEGER NOT NULL,
    daily_status INTEGER NOT NULL
);

