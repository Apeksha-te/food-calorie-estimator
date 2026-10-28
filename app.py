# ============================================================
# app.py - Main Flask Backend for Food Calorie Estimator
# Author: Final Year Project
# Description: Flask server that handles image upload,
#              ML prediction, and database storage
# ============================================================

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3
from datetime import datetime
from predict import predict_food          # our prediction module
from utils import allowed_file, generate_pdf_report
import uuid

# --- App Configuration ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # 16 MB max upload

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================
# DATABASE SETUP
# ============================================================
DB_PATH = 'database.db'

def init_db():
    """Create database tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            filename  TEXT    NOT NULL,
            food_name TEXT    NOT NULL,
            calories  REAL    NOT NULL,
            protein   REAL    NOT NULL,
            carbs     REAL    NOT NULL,
            fat       REAL    NOT NULL,
            confidence REAL   NOT NULL,
            timestamp TEXT    NOT NULL
        )
    ''')
    # Daily calorie tracker table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tracker (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      TEXT    NOT NULL,
            food_name TEXT    NOT NULL,
            calories  REAL    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(filename, food_name, calories, protein, carbs, fat, confidence):
    """Save a prediction result to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO predictions (filename, food_name, calories, protein, carbs, fat, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (filename, food_name, calories, protein, carbs, fat, confidence, timestamp))
    conn.commit()
    conn.close()

def get_all_predictions():
    """Retrieve all predictions from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # returns dict-like rows
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_daily_calories():
    """Get total calories consumed today."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT SUM(calories) FROM daily_tracker WHERE date=?', (today,))
    result = cursor.fetchone()[0]
    conn.close()
    return result or 0

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Upload page."""
    return render_template('upload.html')

@app.route('/about')
def about():
    """About project page."""
    return render_template('about.html')

@app.route('/history')
def history():
    """Prediction history page."""
    records = get_all_predictions()
    daily_cal = get_daily_calories()
    return render_template('history.html', records=records, daily_calories=daily_cal)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle image upload and return prediction.
    Accepts multipart/form-data with key 'image'.
    Returns JSON with food info and nutrition data.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use JPG, PNG, JPEG, or WEBP'}), 400

    # Save file with unique name to avoid collisions
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    # Run ML prediction
    try:
        result = predict_food(filepath)
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

    # Save to DB
    save_prediction(
        filename   = unique_name,
        food_name  = result['food_name'],
        calories   = result['calories'],
        protein    = result['protein'],
        carbs      = result['carbs'],
        fat        = result['fat'],
        confidence = result['confidence']
    )

    # Also add to daily tracker
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO daily_tracker (date, food_name, calories) VALUES (?, ?, ?)',
                   (today, result['food_name'], result['calories']))
    conn.commit()
    conn.close()

    result['image_url'] = f"/static/uploads/{unique_name}"
    return jsonify(result)

@app.route('/api/history')
def api_history():
    """JSON API for history records."""
    records = get_all_predictions()
    return jsonify(records)

@app.route('/api/daily-calories')
def api_daily_calories():
    """Return today's total calories."""
    return jsonify({'total': get_daily_calories()})

@app.route('/api/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a prediction record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE id=?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/clear-history', methods=['DELETE'])
def clear_history():
    """Clear all prediction history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == '__main__':
    init_db()          # create tables if not present
    print("=" * 55)
    print("  AI Food Calorie Estimator - Flask Server")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 55)
    app.run(debug=True, host='0.0.0.0', port=5000)
