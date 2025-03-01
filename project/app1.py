from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Initialize Flask App
app = Flask(__name__)
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn



# Database Initialization
with sqlite3.connect('database.db') as conn:
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    credits INTEGER DEFAULT 20,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    filename TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['credits'] = user['credits']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials!", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    documents = conn.execute("SELECT * FROM documents WHERE user_id = ?", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', user=user, documents=documents)

@app.route('/scan', methods=['GET', 'POST'])
def scan_document():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if session['credits'] <= 0:
            flash("Not enough credits!", "danger")
            return redirect(url_for('dashboard'))

        if 'file' not in request.files:
            flash("No file part!", "danger")
            return redirect(url_for('scan_document'))

        file = request.files['file']
        if file.filename == "":
            flash("No selected file!", "danger")
            return redirect(url_for('scan_document'))

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            conn.execute("INSERT INTO documents (user_id, filename) VALUES (?, ?)", (session['user_id'], filename))
            conn.execute("UPDATE users SET credits = credits - 1 WHERE id = ?", (session['user_id'],))
            conn.commit()
            conn.close()

            session['credits'] -= 1
            flash(f"Document '{filename}' scanned successfully!", "success")
            return redirect(url_for('dashboard'))  # Redirect to prevent resubmission

    return render_template('scan.html')


@app.route('/request_credits', methods=['POST'])
def request_credits():
    if 'user_id' not in session:
        flash("You must be logged in to request credits.", "danger")
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute("UPDATE users SET credits = credits + 10 WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()
    session['credits'] += 10
    flash("10 credits added successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
