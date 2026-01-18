# db_utils.py

import sqlite3

DATABASE = 'sudoku.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_extra_tables():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        difficulty TEXT,
        time_taken INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS saved_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        puzzle TEXT,
        progress TEXT,
        solution TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_puzzle (
        date TEXT PRIMARY KEY,
        puzzle TEXT,
        solution TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        time_taken INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
        username TEXT PRIMARY KEY,
        streak_count INTEGER DEFAULT 0,
        last_played_date TEXT
    )''')

    conn.commit()
    conn.close()
