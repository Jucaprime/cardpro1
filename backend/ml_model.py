import os
import joblib
import pandas as pd
import time
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier
from database import get_db_connection

MODEL_PATH = "models/cards_classifier.pkl"
REGRESSOR_PATH = "models/cards_regressor.pkl"

def initialize_mock_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM training_data")
    row = cursor.fetchone()
    if row['cnt'] == 0:
        mock_data = [
            (2.5, 2.1, 5.0, 50.0, 50.0, 50.0, 50.0, 1.8, 1.9, True, 6.0),
            (1.5, 1.8, 3.5, 50.0, 50.0, 50.0, 50.0, 2.1, 1.7, False, 3.0),
            (3.0, 2.8, 6.0, 50.0, 50.0, 50.0, 50.0, 1.6, 2.2, True, 7.0),
            (1.0, 1.2, 4.0, 50.0, 50.0, 50.0, 50.0, 2.5, 1.5, False, 2.0),
            (2.0, 2.0, 4.5, 50.0, 50.0, 50.0, 50.0, 1.9, 1.9, True, 5.0),
            (2.8, 2.5, 5.5, 50.0, 50.0, 50.0, 50.0, 1.7, 2.0, True, 6.0),
            (1.2, 1.5, 3.8, 50.0, 50.0, 50.0, 50.0, 2.2, 1.6, False, 3.0),
            (2.2, 2.4, 4.8, 50.0, 50.0, 50.0, 50.0, 1.85, 1.85, True, 5.0),
            (1.8, 1.9, 4.2, 50.0, 50.0, 50.0, 50.0, 1.95, 1.8, False, 4.0),
            (3.5, 3.0, 6.5, 50.0, 50.0, 50.0, 50.0, 1.5, 2.4, True, 8.0),
        ]
        cursor.executemany('''
            INSERT INTO training_data 
            (home_cards_avg, away_cards_avg, referee_avg, last3_over_rate, last5_referee_over_rate, home_aggression_trend, away_aggression_trend, odds_over, odds_under, result_is_over, actual_cards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', mock_data)
        conn.commit()
    conn.close()

def train_model():
    start_time = time.time()
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM training_data", conn)
    conn.close()
    
    if len(df) < 5:
        return {"error": "Dados de treinamento insuficientes"}
        
    features = ['home_cards_avg', 'away_cards_avg', 'referee_avg', 'last3_over_rate', 'last5_referee_over_rate', 'home_aggression_trend', 'away_aggression_trend', 'odds_over', 'odds_under']
    X = df[features]
    y = df['result_is_over']
    
    # 1. Train Classifier Ensemble
    try:
        base_model = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=42
        )
        base_model.fit(X, y)
        clf_model = CalibratedClassifierCV(estimator=base_model, method='sigmoid', cv=2)
        clf_model.fit(X, y)
    except Exception as e:
        print(f"XGBoost Classifier falhou, usando RandomForest: {e}")
        base_model = RandomForestClassifier(n_estimators=100, random_state=42)
        base_model.fit(X, y)
        clf_model = CalibratedClassifierCV(estimator=base_model, method='sigmoid', cv=2)
        clf_model.fit(X, y)
    
    joblib.dump(clf_model, MODEL_PATH)
    
    # 2. Train Regressor
    df_reg = df.dropna(subset=['actual_cards'])
    if len(df_reg) >= 5:
        X_reg = df_reg[features]
        y_reg = df_reg['actual_cards']
        try:
            reg_model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42)
            reg_model.fit(X_reg, y_reg)
            joblib.dump(reg_model, REGRESSOR_PATH)
        except Exception as e:
            print(f"XGBoost Regressor falhou: {e}")
            joblib.dump(None, REGRESSOR_PATH)
    else:
        joblib.dump(None, REGRESSOR_PATH)
    
    # Metrics
    y_pred = clf_model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    end_time = time.time()
    
    return {
        "accuracy": float(accuracy * 100),
        "precision": float(precision * 100),
        "recall": float(recall * 100),
        "f1_score": float(f1 * 100),
        "games_learned": len(df),
        "training_time": float(end_time - start_time)
    }

def get_models():
    if not os.path.exists(MODEL_PATH):
        initialize_mock_data()
        train_model()
    clf = joblib.load(MODEL_PATH)
    reg = joblib.load(REGRESSOR_PATH) if os.path.exists(REGRESSOR_PATH) else None
    return clf, reg

def predict_cards(data):
    clf_model, reg_model = get_models()
    
    try:
        ref_impact = data.referee_avg / (data.home_cards_avg + data.away_cards_avg)
    except:
        ref_impact = 0.5
        
    df = pd.DataFrame([{
        'home_cards_avg': data.home_cards_avg,
        'away_cards_avg': data.away_cards_avg,
        'referee_avg': data.referee_avg,
        'last3_over_rate': data.last3_over_rate,
        'last5_referee_over_rate': data.last5_referee_over_rate,
        'home_aggression_trend': data.home_aggression_trend,
        'away_aggression_trend': data.away_aggression_trend,
        'odds_over': data.odds_over,
        'odds_under': data.odds_under
    }])
    
    # 1. Regressor Prediction (Expected Cards)
    if reg_model is not None:
        expected_cards = float(reg_model.predict(df)[0])
    else:
        expected_cards = round((data.home_cards_avg + data.away_cards_avg) * 0.65 + data.referee_avg * 0.35, 1)
        
    # 2. Classifier Prediction
    prob = clf_model.predict_proba(df)[0]
    under_prob = prob[0] * 100
    over_prob = prob[1] * 100
    
    if over_prob > 50:
        prediction = "OVER"
        confidence = over_prob
    else:
        prediction = "UNDER"
        confidence = under_prob
        
    # Inconsistency Logic
    inconsistency_alert = None
    risk_score = 100.0 - confidence
    
    if prediction == "OVER" and expected_cards < 4.5:
        inconsistency_alert = "LOW MATHEMATICAL CONSISTENCY: Expected cards indicate Under, mas o modelo aponta Over."
        confidence = max(50.1, confidence - 15)
        risk_score = min(95.0, risk_score + 40.0)
    elif prediction == "UNDER" and expected_cards > 4.5:
        inconsistency_alert = "LOW MATHEMATICAL CONSISTENCY: Expected cards indicate Over, mas o modelo aponta Under."
        confidence = max(50.1, confidence - 15)
        risk_score = min(95.0, risk_score + 40.0)
        
    # Expected Value
    ev_over = (over_prob / 100) * data.odds_over - 1
    ev_under = (under_prob / 100) * data.odds_under - 1
    ev_target = ev_over if prediction == "OVER" else ev_under
    
    # Value Classification
    if ev_target > 0.15:
        value_label = "🔥 ALTO VALOR"
    elif ev_target > 0.05:
        value_label = "✅ VALOR MÉDIO"
    else:
        value_label = "⚠ BAIXO VALOR"
        
    # Edge Score (0-100 scale approximation based on formula: prob * ev * conf)
    edge_score = min(100.0, max(0.0, (max(over_prob, under_prob)/100) * max(0.01, ev_target) * (confidence/100) * 1000))
    
    if edge_score >= 80:
        quality = "Aposta de Elite"
    elif edge_score >= 60:
        quality = "Aposta Forte"
    elif edge_score >= 40:
        quality = "Razoável"
    else:
        quality = "Evitar"
        
    value_label = f"{value_label} | {quality}"
    
    # Multi-lines Probability generation using Poisson
    def poisson_prob(k, lam):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)
        
    def calc_under_line(lam, line):
        k_max = int(line)
        return sum(poisson_prob(k, lam) for k in range(k_max + 1)) * 100
        
    multi_lines = {
        "4.5": {
            "under": calc_under_line(expected_cards, 4.5),
            "over": 100 - calc_under_line(expected_cards, 4.5)
        },
        "5.5": {
            "under": calc_under_line(expected_cards, 5.5),
            "over": 100 - calc_under_line(expected_cards, 5.5)
        },
        "6.5": {
            "under": calc_under_line(expected_cards, 6.5),
            "over": 100 - calc_under_line(expected_cards, 6.5)
        }
    }
        
    explanation = f"Modelo Híbrido: Previsão exata de {expected_cards:.1f} cartões (XGBRegressor). Impacto do árbitro: {ref_impact:.2f}. Classificador aponta {prediction} com {confidence:.1f}% de confiança calibrada."
    
    base_est = getattr(clf_model, 'estimator', clf_model)
    model_name = type(base_est).__name__
    
    algorithm_log = {
        "model_type": f"Hybrid: {model_name} + XGBRegressor",
        "edge_score": edge_score,
        "referee_impact": ref_impact
    }
        
    return {
        "prediction": prediction,
        "confidence": float(confidence),
        "under_prob": float(under_prob),
        "over_prob": float(over_prob),
        "expected_cards": float(expected_cards),
        "explanation": explanation,
        "algorithm_log": algorithm_log,
        "ev_over": float(ev_over),
        "ev_under": float(ev_under),
        "risk_score": float(risk_score),
        "inconsistency_alert": inconsistency_alert,
        "edge_score": float(edge_score),
        "value_label": value_label,
        "multi_lines": multi_lines
    }
