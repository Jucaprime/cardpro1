import sqlite3
import os

DB_PATH = "cardedge.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT DEFAULT 'Casa',
            away_team TEXT DEFAULT 'Fora',
            home_cards_avg REAL,
            away_cards_avg REAL,
            referee_avg REAL,
            last3_over_rate REAL DEFAULT 50.0,
            last5_referee_over_rate REAL DEFAULT 50.0,
            home_aggression_trend REAL DEFAULT 50.0,
            away_aggression_trend REAL DEFAULT 50.0,
            odds_over REAL,
            odds_under REAL,
            prediction TEXT,
            confidence REAL,
            under_prob REAL,
            over_prob REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Feedbacks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            is_correct BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prediction_id) REFERENCES predictions(id)
        )
    ''')
    
    # Training Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT DEFAULT 'Casa',
            away_team TEXT DEFAULT 'Fora',
            home_cards_avg REAL,
            away_cards_avg REAL,
            referee_avg REAL,
            last3_over_rate REAL DEFAULT 50.0,
            last5_referee_over_rate REAL DEFAULT 50.0,
            home_aggression_trend REAL DEFAULT 50.0,
            away_aggression_trend REAL DEFAULT 50.0,
            odds_over REAL,
            odds_under REAL,
            result_is_over BOOLEAN,
            actual_cards REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Simple migration: Add home_team and away_team if they do not exist
    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN home_team TEXT DEFAULT 'Casa'")
        cursor.execute("ALTER TABLE predictions ADD COLUMN away_team TEXT DEFAULT 'Fora'")
    except sqlite3.OperationalError:
        pass # Columns already exist

    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN last3_over_rate REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE predictions ADD COLUMN last5_referee_over_rate REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE predictions ADD COLUMN home_aggression_trend REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE predictions ADD COLUMN away_aggression_trend REAL DEFAULT 50.0")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE training_data ADD COLUMN last3_over_rate REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE training_data ADD COLUMN last5_referee_over_rate REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE training_data ADD COLUMN home_aggression_trend REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE training_data ADD COLUMN away_aggression_trend REAL DEFAULT 50.0")
        cursor.execute("ALTER TABLE training_data ADD COLUMN actual_cards REAL")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE feedbacks ADD COLUMN actual_cards REAL")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

if not os.path.exists(DB_PATH):
    init_db()
else:
    init_db() # Run init_db anyway to trigger the migration step
