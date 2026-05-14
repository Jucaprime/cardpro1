from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import database
import ml_model

app = FastAPI(title="Card Pro")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run init DB on startup
database.init_db()
# Ensure model exists
ml_model.get_models()

class PredictRequest(BaseModel):
    home_team: Optional[str] = "Time Casa"
    away_team: Optional[str] = "Time Fora"
    home_cards_avg: float
    away_cards_avg: float
    referee_avg: float
    last3_over_rate: Optional[float] = 50.0
    last5_referee_over_rate: Optional[float] = 50.0
    home_aggression_trend: Optional[float] = 50.0
    away_aggression_trend: Optional[float] = 50.0
    odds_over: float
    odds_under: float

class PredictResponse(BaseModel):
    id: Optional[int]
    prediction: str
    confidence: float
    under_probability: float
    over_probability: float
    expected_cards: float
    explanation: str
    algorithm_log: dict
    ev_over: float = 0.0
    ev_under: float = 0.0
    risk_score: float = 0.0
    inconsistency_alert: Optional[str] = None
    edge_score: float = 0.0
    value_label: str = ""
    multi_lines: dict = {}

class FeedbackRequest(BaseModel):
    prediction_id: int
    is_correct: Optional[bool] = None
    actual_cards: Optional[float] = None

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    result = ml_model.predict_cards(req)
    
    # Save prediction to DB
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions 
        (home_team, away_team, home_cards_avg, away_cards_avg, referee_avg, 
         last3_over_rate, last5_referee_over_rate, home_aggression_trend, away_aggression_trend,
         odds_over, odds_under, prediction, confidence, under_prob, over_prob)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (req.home_team, req.away_team, req.home_cards_avg, req.away_cards_avg, req.referee_avg, 
          req.last3_over_rate, req.last5_referee_over_rate, req.home_aggression_trend, req.away_aggression_trend,
          req.odds_over, req.odds_under, 
          result["prediction"], result["confidence"], result["under_prob"], result["over_prob"]))
    pred_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": pred_id,
        "prediction": result["prediction"] + " 4.5", # Mock line 4.5
        "confidence": result["confidence"],
        "under_probability": result["under_prob"],
        "over_probability": result["over_prob"],
        "expected_cards": result["expected_cards"],
        "explanation": result["explanation"],
        "algorithm_log": result["algorithm_log"],
        "ev_over": result.get("ev_over", 0.0),
        "ev_under": result.get("ev_under", 0.0),
        "risk_score": result.get("risk_score", 0.0),
        "inconsistency_alert": result.get("inconsistency_alert", None),
        "edge_score": result.get("edge_score", 0.0),
        "value_label": result.get("value_label", ""),
        "multi_lines": result.get("multi_lines", {})
    }

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Insert feedback
    cursor.execute("INSERT INTO feedbacks (prediction_id, is_correct, actual_cards) VALUES (?, ?, ?)", (req.prediction_id, req.is_correct, req.actual_cards))
    
    # Retrieve prediction details to add to training data
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (req.prediction_id,))
    pred = cursor.fetchone()
    
    if pred:
        # Determine actual result based on prediction and feedback if actual_cards is not provided
        result_is_over = False
        if req.actual_cards is not None:
            result_is_over = req.actual_cards > 4.5
        elif req.is_correct is not None:
            pred_is_over = pred["prediction"] == "OVER"
            result_is_over = pred_is_over if req.is_correct else not pred_is_over
            
        cursor.execute('''
            INSERT INTO training_data 
            (home_team, away_team, home_cards_avg, away_cards_avg, referee_avg, 
             last3_over_rate, last5_referee_over_rate, home_aggression_trend, away_aggression_trend,
             odds_over, odds_under, result_is_over, actual_cards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pred.get("home_team", "Casa"), pred.get("away_team", "Fora"), pred["home_cards_avg"], pred["away_cards_avg"], pred["referee_avg"], 
              pred.get("last3_over_rate", 50.0), pred.get("last5_referee_over_rate", 50.0), pred.get("home_aggression_trend", 50.0), pred.get("away_aggression_trend", 50.0),
              pred["odds_over"], pred["odds_under"], result_is_over, req.actual_cards))
        
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Feedback received and added to training data."}

@app.post("/train")
def train():
    stats = ml_model.train_model()
    return stats

@app.get("/history")
def get_history():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, f.is_correct 
        FROM predictions p 
        LEFT JOIN feedbacks f ON p.id = f.prediction_id
        ORDER BY p.id DESC LIMIT 50
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/stats")
def get_stats():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM training_data")
    total_trained = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as total FROM feedbacks WHERE is_correct = 1")
    correct_preds = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as total FROM feedbacks")
    total_feedbacks = cursor.fetchone()["total"]
    
    conn.close()
    
    accuracy = (correct_preds / total_feedbacks * 100) if total_feedbacks > 0 else 0
    
    return {
        "accuracy": round(accuracy, 1),
        "games_learned": total_trained
    }
