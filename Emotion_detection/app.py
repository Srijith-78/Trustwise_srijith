from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.db'
HUGGINGFACE_API_KEY = "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"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                toxicity_label TEXT,
                toxicity_score REAL,
                emotion_label TEXT,
                emotion_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def fetch_model_result(endpoint, input_text):
    url = f'https://api-inference.huggingface.co/models/{endpoint}'
    headers = {'Authorization': f'Bearer {HUGGINGFACE_API_KEY}'}
    payload = {"inputs": input_text}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching model result: {e}")
        return None


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Text is required.'}), 400
    
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text field is missing in the request body.'}), 400
    
    toxicity = fetch_model_result('s-nlp/roberta_toxicity_classifier', text)
    emotion = fetch_model_result('SamLowe/roberta-base-go_emotions', text)

    if not toxicity or not emotion:
        return jsonify({'error': 'Error fetching model results.'}), 500

    if isinstance(emotion, list) and len(emotion) > 0:
        emotions = emotion[0]
        top_emotions = sorted(emotions, key=lambda x: x['score'], reverse=True)[:5] 
        emotion_labels = [e['label'] for e in top_emotions]
        emotion_scores = [e['score'] for e in top_emotions]
    else:
        return jsonify({'error': 'Invalid emotion response structure.'}), 500
    max_toxicity = sorted(toxicity[0], key=lambda x: x['score'], reverse=True)[:5]
    toxicity_labels = [t['label'] for t in max_toxicity]
    toxicity_scores = [t['score'] for t in max_toxicity]

    log_to_database(text, emotion_labels[0], emotion_scores[0], toxicity_labels[0], toxicity_scores[0])
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT * FROM logs ORDER BY timestamp")
        logs = [{
            "id": row[0], 
            "text": row[1], 
            "toxicity_label": row[2], 
            "toxicity_score": round(row[3], 2), 
            "emotion_label": row[4], 
            "emotion_score": round(row[5], 2), 
            "timestamp": row[6]
        } for row in cursor.fetchall()]

    return jsonify({
        'toxicity': {'label': toxicity_labels[0], 'score': round(toxicity_scores[0], 2)},
        'emotion': {'label': emotion_labels[0], 'score': round(emotion_scores[0], 2)},
        'toxicity_labels': toxicity_labels,
        'toxicity_scores': toxicity_scores,
        'emotion_labels': emotion_labels,
        'emotion_scores': emotion_scores,
        'logs': logs 
    })

import datetime

def log_to_database(text, toxicity_label, toxicity_score, emotion_label, emotion_score):
    toxicity_score = round(toxicity_score, 2)
    emotion_score = round(emotion_score, 2)
    timestamp = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            INSERT INTO logs (text, toxicity_label, toxicity_score, emotion_label, emotion_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, toxicity_label, toxicity_score, emotion_label, emotion_score, timestamp))

@app.route('/logs', methods=['GET'])
def get_logs():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = [{
            "id": row[0], 
            "text": row[1], 
            "toxicity_label": row[2], 
            "toxicity_score": round(row[3], 2),
            "emotion_label": row[4], 
            "emotion_score": round(row[5], 2),
            "timestamp": row[6]
        } for row in cursor.fetchall()]
    return jsonify(logs)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)