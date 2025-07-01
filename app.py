from flask import Flask, render_template, request, redirect, flash
import sqlite3
from decimal import Decimal, InvalidOperation
import re
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  

DB_NAME = 'donations.db'


def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                amount REAL NOT NULL,
                message TEXT
            )
        ''')
        conn.commit()
        conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        amount = request.form['amount'].strip()
        message = request.form['message'].strip()

        
        if not name or not email or not amount:
            flash("Name, email, and amount are required.", "danger")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address.", "danger")
        else:
            try:
                amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
                if amount_decimal <= 0:
                    raise InvalidOperation()
            except InvalidOperation:
                flash("Amount must be a positive number.", "danger")
            else:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute(
                    'INSERT INTO donations (name, email, amount, message) VALUES (?, ?, ?, ?)',
                    (name, email, float(amount_decimal), message)
                )
                conn.commit()
                conn.close()
                flash("Donation submitted successfully!", "success")
                return redirect('/')

    
    conn = get_db_connection()
    donations = conn.execute('SELECT * FROM donations ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', donations=donations)

if __name__ == '__main__':
    app.run(debug=True)
