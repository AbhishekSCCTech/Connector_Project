import re
from datetime import datetime
import mysql.connector
import os
import traceback

# ------------------- Log Patterns -------------------
log_pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2}\.\d{3})\s+\+\d{2}:\d{2}\s+"
    r"\[(?P<level>\w+)\]\s+"
    r"Methodname:\s+\[(?P<operation>Read|Write)\s*:\s*(?P<method>[^\]]+)\]\s+"
    r"Message:\s+(?P<message>.+)"
)

model_object_pattern = re.compile(
    r"Unsupported ModelObject\s*:\s*(?P<model_object>[\w\.]+)\s*(?P<guid>[a-f0-9\-]+)?"
)

read_failed_pattern = re.compile(
    r"FailedItemsToReadObjects\s*:\s*(?P<failed_item>.+)"
)

# --- Exchange Name Patterns ---
exchange_name_pattern_1 = re.compile(
    r"Exchange Name\s*:\s*(?P<exchange_name>.+?)\s+Exchange ID"
)
exchange_name_pattern_2 = re.compile(
    r"Exchange creation started.*?\|\s*Exchange Name\s*:\s*(?P<exchange_name>\S+)"
)

# ------------------- Process Function -------------------
def process_log_lines(filepath, lines):
    print("Connecting to DB...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="log_db"
    )
    cursor = conn.cursor()

    sql = """
        INSERT INTO logger_Table (
            filename, log_date, log_time, log_level, operation_type, method,
            message_type, model_object, guid, failed_item, message, raw_message, exchange_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    filename = os.path.basename(filepath)
    print(f"\n[INFO] Processing file: {filename}")
    current_exchange_name = None

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        print(f"\n[Line {idx+1}] Raw line: {line}")

        try:
            match = log_pattern.match(line)
            if match:
                print(f"[Line {idx+1}] Regex MATCHED ✅")
                data = match.groupdict()

                date_obj = datetime.strptime(data['date'], "%Y-%m-%d").date()
                time_obj = datetime.strptime(data['time'], "%H:%M:%S.%f").time()

                log_level = data['level']
                operation_type = data['operation']
                method = data['method']
                message = data['message']

                message_type = None
                model_object = None
                guid = None
                failed_item = None

                # ✅ Try both patterns to capture exchange name
                exch_match1 = exchange_name_pattern_1.search(message)
                exch_match2 = exchange_name_pattern_2.search(message)

                if exch_match1:
                    current_exchange_name = exch_match1.group("exchange_name").strip()
                    print(f"[Line {idx+1}] ✅ Exchange Name (Read format) FOUND: '{current_exchange_name}'")
                elif exch_match2:
                    current_exchange_name = exch_match2.group("exchange_name").strip()
                    print(f"[Line {idx+1}] ✅ Exchange Name (Write format) FOUND: '{current_exchange_name}'")
                else:
                    print(f"[Line {idx+1}] ❌ No exchange name matched for message: {message}")

                # Nested model_object parsing
                if "Unsupported ModelObject" in message:
                    model_match = model_object_pattern.search(message)
                    if model_match:
                        print(f"[Line {idx+1}] ModelObject MATCHED ✅")
                        model_object = model_match.group('model_object')
                        guid = model_match.group('guid')
                        message_type = "Unsupported ModelObject"

                elif "FailedItemsToReadObjects" in message:
                    failed_match = read_failed_pattern.search(message)
                    if failed_match:
                        print(f"[Line {idx+1}] FailedItemsToReadObjects MATCHED ✅")
                        failed_item = failed_match.group('failed_item')
                        message_type = "FailedItemsToReadObjects"

                values = (
                    filename, date_obj, time_obj, log_level, operation_type, method,
                    message_type, model_object, guid, failed_item, message, line, current_exchange_name
                )

                print(f"[Line {idx+1}] Inserting exchange_name: {current_exchange_name}")
                cursor.execute(sql, values)
                print(f"[Line {idx+1}] Insert SUCCESS ✅")

            else:
                print(f"[Line {idx+1}] Regex did NOT match ❌")

        except Exception as e:
            print(f"[Line {idx+1}] Error processing this line ❌")
            traceback.print_exc()

    conn.commit()
    cursor.close()
    conn.close()
    print("[INFO] DB connection closed ✅")
