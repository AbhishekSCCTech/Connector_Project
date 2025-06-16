from flask import Flask, request, jsonify, render_template
import mysql.connector
from import_logs import start_watching
from log_parser import process_log_lines

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="log_db"
    )

@app.route("/details")
def details():
    filename = request.args.get("filename")
    level = request.args.get("level")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT log_date, log_time, message
        FROM logger_Table
        WHERE filename = %s AND log_level = %s
    """
    cursor.execute(query, (filename, level))
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(logs)

@app.route("/visualization")
def visualization():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM logger_Table")
    rows = cursor.fetchall()
    print("Visualization route working!")

    cursor.close()
    conn.close()
    
    return render_template("visualization.html", rows=rows)

if __name__ == "__main__":
    LOG_FOLDER = r"F:\Log viwer Project\TeklaExternalLogFiles"
    start_watching(LOG_FOLDER, process_log_lines)
    app.run(port=5021, debug=True)
