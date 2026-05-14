import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("ERRO CRÍTICO: DATABASE_URL não definida no arquivo .env. Crie uma conta no Supabase e configure a URL.")
        
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    if not DATABASE_URL:
        print("Aviso: DATABASE_URL não definida, o banco PostgreSQL não será inicializado.")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Predictions table (PostgreSQL usa SERIAL em vez de AUTOINCREMENT)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            prediction_id INTEGER,
            is_correct BOOLEAN,
            actual_cards REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prediction_id) REFERENCES predictions(id)
        )
    ''')
    
    # Training Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_data (
            id SERIAL PRIMARY KEY,
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
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Erro ao conectar/inicializar banco Supabase: {e}")
