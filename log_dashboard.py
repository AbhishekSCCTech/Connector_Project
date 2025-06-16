from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="log_db"
    )

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logger_Table LIMIT 1000")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True, port=5054)
