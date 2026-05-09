import sqlite3

def create_db():
    conn = sqlite3.connect("fall_detection.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        event_type TEXT,
        body_angle REAL,
        risk_level TEXT,
        recovery_status TEXT,
        alert_sent TEXT,
        snapshot_path TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_event(data):
    conn = sqlite3.connect("fall_detection.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO events 
    (date, time, event_type, body_angle, risk_level, recovery_status, alert_sent, snapshot_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()