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
    #cursor.execute("SELECT * FROM logger_Table LIMIT 1000")
    cursor.execute("SELECT id, filename, log_date, log_time, log_level, exchange_name, operation_type, method, message_type, model_object, message FROM logger_Table_New2")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", rows=rows)

if __name__ == "__main__":
    app.run(port=5025, debug=True)
