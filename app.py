from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DB_NAME = 'database.db'

def fetch_jobs():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    jobs = conn.execute('SELECT * FROM jobs ORDER BY id DESC').fetchall()
    conn.close()
    return jobs

@app.route('/')
def index():
    jobs = fetch_jobs()
    return render_template('index.html', jobs=jobs)

if __name__ == '__main__':
    app.run(debug=True)
