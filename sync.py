import csv
import os
import shutil

import requests

# Check if manual run with force input
force_sync = os.environ.get("INPUT_FORCE", "false").lower() == "true"

# CONFIG
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwBTqxi1ifz-d8MKHKErzTH7TwdVMpGwklnUg-l3a7zyIXMJdrew8Xgr8T22M-GMhpFhgxrPl9eMrR/pub?output=csv"
BOILERPLATE_FILE = "boilerplate.java"
LAST_SYNC_FILE = "last_sync.txt"
BASE_DIR = "."

def read_last_synced_id():
    if not os.path.exists(LAST_SYNC_FILE) or force_sync:
        return "Q000"
    with open(LAST_SYNC_FILE, "r") as f:
        return f.read().strip()

def write_last_synced_id(qid):
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(qid)

def format_class_name(title):
    return title.replace(" ", "").replace("-", "_")

def generate_code_file(qid, title, description):
    folder_name = f"{qid}_{format_class_name(title)}"
    file_name = f"{qid}_{format_class_name(title)}.java"
    folder_path = os.path.join(BASE_DIR, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(BOILERPLATE_FILE, "r") as bp:
        code = bp.read()

    class_name = f"{qid}_{format_class_name(title)}"
    code = code.replace("class Main", f"class {class_name}")

    # Add title and description as header comment
    header_comment = f"""/*
 * QID: {qid}
 * Title: {title}
 * Description: {description}
 */
"""

    full_code = f"{header_comment}\n{code}"

    with open(os.path.join(folder_path, file_name), "w") as f:
        f.write(full_code)

def main():
    response = requests.get(CSV_URL)
    decoded = response.content.decode("utf-8")
    reader = csv.reader(decoded.splitlines())

    rows = list(reader)
    if not rows or len(rows) < 2:
        print("No data found.")
        return

    header = rows[0]
    data_rows = rows[1:]

    last_id = read_last_synced_id()
    new_entries = []

    for row in data_rows:
        if len(row) < 3:
            print(f"Skipping malformed row: {row}")
            continue

        qid = row[0].strip()
        title = row[1].strip()
        description = row[2].strip()

        if force_sync or qid > last_id:
            new_entries.append((qid, title, description))

    if not new_entries:
        print("No new questions to sync.")
        return

    for qid, title, description in new_entries:
        print(f"Syncing: {qid} - {title}")
        generate_code_file(qid, title, description)

    write_last_synced_id(new_entries[-1][0])
    print("Sync complete.")

if __name__ == "__main__":
    main()
