import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "bot.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL DEFAULT 0,
            description TEXT DEFAULT '',
            collection_count INTEGER DEFAULT 0,
            enabled INTEGER DEFAULT 0,
            channel_id TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Created',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            transaction_id TEXT UNIQUE,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            verified_at TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id TEXT NOT NULL UNIQUE,
            category_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            invite_link TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS demo_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE INDEX IF NOT EXISTS idx_orders_user
        ON orders(user_id);

        CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status);
        """)

if __name__ == "__main__":
    initialize_database()
    print("SQLite Database initialized successfully!")
