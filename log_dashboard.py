from flask import Flask, render_template,request, send_file, redirect, url_for
import mysql.connector
from typing import Any
import os
app = Flask(__name__)

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

@app.route("/", methods=["GET"])
def index():
    # Filters from request
    exchange_name = request.args.get("exchange_name")
    operation_type = request.args.get("operation_type")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    # Query for log data
    query = "SELECT id, filename, log_date, log_time, log_level, exchange_name, operation_type, method, model_object, message FROM logger_Table_New2 WHERE 1=1"
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

    cursor.execute("SELECT DISTINCT exchange_name FROM logger_Table_New2 WHERE exchange_name IS NOT NULL AND exchange_name != ''")
    exchange_names = []
    for row in cursor.fetchall():
        if isinstance(row, dict) and "exchange_name" in row:
            exchange_names.append(row["exchange_name"])
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exchange_names.append(row[0])
    # print("Exchange names:", exchange_names)  # Remove or comment out debug print

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Folder dropdown logic
    root_path = r"F:\Log viwer Project\Tekla-Connector-2022\Tekla-Connector-2022\logs"
    subfolders = ["GeometryLogs", "HttpLogs", "DesignTranslator", "RequestLogs", "SkippedElement-Reports"]
    selected_folder = request.args.get("log_folder", subfolders[0])
    txt_files = []
    folder_path = os.path.join(root_path, selected_folder)
    if os.path.exists(folder_path):
        txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    return render_template(
        "dashboard.html",
        rows=rows,
        exchange_names=exchange_names,
        selected_exchange=exchange_name,
        subfolders=subfolders,
        selected_folder=selected_folder,
        txt_files=txt_files
    )

@app.route("/view_log")
def view_log():
    folder = request.args.get("folder")
    filename = request.args.get("filename")
    if not folder or not filename:
        return "Missing folder or filename parameter", 400

    root_path = r"C:\Users\Abhishek Suryawanshi\Downloads\Tekla-Connector-2022\Tekla-Connector-2022\logs"
    file_path = os.path.join(root_path, folder, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return render_template("view_log.html", filename=filename, lines=lines)

if __name__ == "__main__":
    app.run(port=5025, debug=True)
