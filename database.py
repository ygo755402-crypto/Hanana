import sqlite3
from pathlib import Path

DB = "knowledge.db"

def connect():
    return sqlite3.connect(DB)

def create_database():
    db = connect()
    db.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
        USING fts5(text, content='knowledge', content_rowid='id')
    """)
    db.execute("""
        CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
            INSERT INTO knowledge_fts(rowid, text) VALUES (new.id, new.text);
        END
    """)
    db.execute("""
        CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
            INSERT INTO knowledge_fts(knowledge_fts, rowid, text)
            VALUES ('delete', old.id, old.text);
        END
    """)
    db.commit()
    db.close()

def import_file(filename="knowledge.txt"):
    create_database()
    db = connect()
    db.execute("DELETE FROM knowledge")
    db.execute("DELETE FROM knowledge_fts")
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(filename)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            if text:
                db.execute("INSERT INTO knowledge(text) VALUES (?)", (text,))
    db.commit()
    db.close()

def all_text():
    db = connect()
    rows = db.execute("SELECT id, text FROM knowledge").fetchall()
    db.close()
    return rows

def search_fts(query, limit=8):
    db = connect()
    try:
        rows = db.execute("""
            SELECT knowledge.id, knowledge.text, bm25(knowledge_fts) AS score
            FROM knowledge_fts
            JOIN knowledge ON knowledge.id = knowledge_fts.rowid
            WHERE knowledge_fts MATCH ?
            ORDER BY score
            LIMIT ?
        """, (query, limit)).fetchall()
    except sqlite3.OperationalError:
        rows = []
    db.close()
    return rows
