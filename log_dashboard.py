from flask import Flask, render_template,request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="log_db"
    )

"""@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #cursor.execute("SELECT * FROM logger_Table LIMIT 1000")
    cursor.execute("SELECT id, filename, log_date, log_time, log_level, exchange_name, operation_type, method, message_type, model_object, message FROM logger_Table_New2")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", rows=rows)
    """

from flask import Flask, render_template, request
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
    # Filters from request
    exchange_name = request.args.get("exchange_name")
    operation_type = request.args.get("operation_type")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    # Query for log data
    query = "SELECT id, filename, log_date, log_time, log_level, exchange_name, operation_type, method, message_type, model_object, message FROM logger_Table_New2 WHERE 1=1"
    params = []

    if exchange_name:
        query += " AND exchange_name = %s"
        params.append(exchange_name)
    if operation_type:
        query += " AND operation_type = %s"
        params.append(operation_type)
    if from_date:
        query += " AND log_date >= %s"
        params.append(from_date)
    if to_date:
        query += " AND log_date <= %s"
        params.append(to_date)

    # Connect and fetch data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT DISTINCT exchange_name FROM log_Tekla_Table WHERE exchange_name IS NOT NULL AND exchange_name != ''")
    exchange_names = [row["exchange_name"] for row in cursor.fetchall()]

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("dashboard.html", rows=rows, exchange_names=exchange_names, selected_exchange=exchange_name)

if __name__ == "__main__":
    app.run(port=5025, debug=True)
