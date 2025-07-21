from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv, os, json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'nagyontitkosszoveg'

CSV_FILE = 'data/adatok.csv'
USER_FILE = 'users.json'

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    is_logged_in = 'username' in session
    return render_template('index.html', rows=rows, logged_in=is_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        return "Hibás felhasználónév vagy jelszó!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
@login_required
def update():
    data = request.json['data']
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return jsonify({"status": "success"})

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        file.save(CSV_FILE)
        return redirect(url_for('index'))
    return "Hibás fájlformátum – csak CSV engedélyezett."

if __name__ == '__main__':
    app.run(debug=True)