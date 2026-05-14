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

DATA_DIR = os.environ.get("DATA_DIR", ".")
MODEL_DIR = os.path.join(DATA_DIR, "models")
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "cards_classifier.pkl")
REGRESSOR_PATH = os.path.join(MODEL_DIR, "cards_regressor.pkl")

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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        
    # 2. Multi-lines Probability generation using Poisson
    def poisson_prob(k, lam):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)
        
    def calc_under_line(lam, line):
        k_max = int(line)
        return sum(poisson_prob(k, lam) for k in range(k_max + 1)) * 100
        
    poisson_under_45 = calc_under_line(expected_cards, 4.5)
    poisson_over_45 = 100.0 - poisson_under_45
    
    multi_lines = {
        "4.5": {"under": poisson_under_45, "over": poisson_over_45},
        "5.5": {"under": calc_under_line(expected_cards, 5.5), "over": 100.0 - calc_under_line(expected_cards, 5.5)},
        "6.5": {"under": calc_under_line(expected_cards, 6.5), "over": 100.0 - calc_under_line(expected_cards, 6.5)}
    }

    # 3. Classifier Prediction
    prob = clf_model.predict_proba(df)[0]
    clf_under = prob[0] * 100.0
    clf_over = prob[1] * 100.0
    
    # 4. Consensus Engine Components
    # Transform expected_cards into an Over % probability using sigmoid curve
    reg_over = 100.0 / (1.0 + math.exp(-(expected_cards - 4.5)))
    reg_under = 100.0 - reg_over
    
    base_over = (clf_over + poisson_over_45) / 2.0
    base_under = (clf_under + poisson_under_45) / 2.0
    
    raw_ev_over = (base_over / 100.0) * data.odds_over - 1.0
    raw_ev_under = (base_under / 100.0) * data.odds_under - 1.0
    
    # EV Score normalized (e.g. 50% ROI = 100 score)
    ev_score_over = min(100.0, max(0.0, raw_ev_over * 200.0))
    ev_score_under = min(100.0, max(0.0, raw_ev_under * 200.0))
    
    # 5. Weighted Final Score
    final_over_score = (clf_over * 0.35) + (reg_over * 0.30) + (poisson_over_45 * 0.25) + (ev_score_over * 0.10)
    final_under_score = (clf_under * 0.35) + (reg_under * 0.30) + (poisson_under_45 * 0.25) + (ev_score_under * 0.10)
    
    # Normalize back to 100%
    total_score = final_over_score + final_under_score
    final_over_prob = (final_over_score / total_score) * 100.0 if total_score > 0 else 50.0
    final_under_prob = 100.0 - final_over_prob
    
    # 6. Mandatory Rules (Hard Mathematical Conflict Override)
    inconsistency_alert = None
    if expected_cards <= 3.0 and poisson_over_45 < 15.0 and final_over_prob > 50.0:
        inconsistency_alert = "HARD MATHEMATICAL CONFLICT: Expected cards too low for an OVER prediction. Blocked."
        final_over_prob = min(final_over_prob, 30.0)
        final_under_prob = 100.0 - final_over_prob
    elif expected_cards >= 6.0 and poisson_under_45 < 15.0 and final_under_prob > 50.0:
        inconsistency_alert = "HARD MATHEMATICAL CONFLICT: Expected cards too high for an UNDER prediction. Blocked."
        final_under_prob = min(final_under_prob, 30.0)
        final_over_prob = 100.0 - final_under_prob
        
    # 7. Consistency Score & Initial Decision
    consistency_score = max(0.0, 100.0 - abs(clf_over - poisson_over_45))
    
    if final_over_prob > 50.0:
        prediction = "OVER"
        confidence = final_over_prob
        target_ev = raw_ev_over
    else:
        prediction = "UNDER"
        confidence = final_under_prob
        target_ev = raw_ev_under
        
    # Confidence Penalty for low consistency
    if consistency_score < 40.0:
        confidence = max(50.1, confidence - 10.0)
        if not inconsistency_alert:
            inconsistency_alert = f"LOW CONSISTENCY ({consistency_score:.1f}/100): Mathematical models strongly disagree with the AI classifier."
            
    # 8. Decision Layer Professional
    if confidence >= 70.0 and consistency_score >= 60.0:
        decision_layer = "Strong Consensus"
    elif confidence >= 55.0:
        decision_layer = "Weak Consensus"
    else:
        decision_layer = "No Consensus"
        
    # Recalculate Risk Score
    risk_score = 100.0 - confidence + (100.0 - consistency_score) * 0.3
    risk_score = min(100.0, max(0.0, risk_score))
    
    # 9. Quantitative Final Score / Value Classification
    if target_ev > 0.15:
        value_label = "🔥 ALTO VALOR"
    elif target_ev > 0.05:
        value_label = "✅ VALOR MÉDIO"
    else:
        value_label = "⚠ BAIXO VALOR"
        
    edge_score = min(100.0, max(0.0, (confidence/100.0) * (consistency_score/100.0) * max(0.01, target_ev) * 1000.0))
    
    if edge_score >= 80.0:
        quality = "Aposta de Elite"
    elif edge_score >= 60.0:
        quality = "Aposta Forte"
    elif edge_score >= 40.0:
        quality = "Razoável"
    else:
        quality = "Evitar"
        
    value_label = f"{value_label} | {quality}"
    
    explanation = f"Consensus Engine ({decision_layer}): Confiança final {confidence:.1f}%. Consistência do modelo: {consistency_score:.1f}/100. "
    explanation += f"Distribuição: XGBClassifier aponta {clf_over:.1f}% Over, enquanto Poisson calcula {poisson_over_45:.1f}% Over baseado em {expected_cards:.1f} cartões esperados."
    
    base_est = getattr(clf_model, 'estimator', clf_model)
    model_name = type(base_est).__name__
    
    algorithm_log = {
        "model_type": f"Consensus: {model_name} + XGBRegressor + Poisson",
        "edge_score": edge_score,
        "referee_impact": ref_impact,
        "consistency_score": consistency_score,
        "decision_layer": decision_layer,
        "clf_over": clf_over,
        "poisson_over": poisson_over_45,
        "reg_over": reg_over
    }
        
    return {
        "prediction": prediction,
        "confidence": float(confidence),
        "under_prob": float(final_under_prob),
        "over_prob": float(final_over_prob),
        "expected_cards": float(expected_cards),
        "explanation": explanation,
        "algorithm_log": algorithm_log,
        "ev_over": float(raw_ev_over),
        "ev_under": float(raw_ev_under),
        "risk_score": float(risk_score),
        "inconsistency_alert": inconsistency_alert,
        "edge_score": float(edge_score),
        "value_label": value_label,
        "multi_lines": multi_lines
    }
