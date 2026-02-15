"""
This Python script is used to start a local web application
built using Flask to load the llm output, display query results,
scrape and load new records into a postgresql database and update
query analysis as required.
"""

import load_data as ld
import query_data as qd
import scrape as sd
import subprocess
import sys

import psycopg

from flask import Flask, render_template, get_flashed_messages, request, jsonify

app = Flask(__name__)   # Create Flask app instance
app.secret_key = "dev"  # secret key to flash message
LAST_RESULTS = []
PULL_DATA_PROCESS = None


def pull_data_busy():
    global PULL_DATA_PROCESS
    if PULL_DATA_PROCESS is None:
        return False
    if PULL_DATA_PROCESS.poll() is None:
        return True
    PULL_DATA_PROCESS = None
    return False


def start_pull_worker():
    global PULL_DATA_PROCESS
    PULL_DATA_PROCESS = subprocess.Popen(
        [sys.executable, __file__, "--run-pull-job"],
    )


def run_pull_job():
    rows = sd.scrape_data(
        "https://www.thegradcafe.com/survey/",
        max_pages=5,
    )
    new_cleaned_file = "new_only.json"
    sd.save_data(rows, new_cleaned_file)
    ld.load(new_cleaned_file)


def perform_update_analysis():
    global LAST_RESULTS
    # Force next /analysis load to execute fresh queries.
    LAST_RESULTS = []

# Connect URL route '/' to index.html
@app.route('/')
@app.route('/analysis')
def index():
    global LAST_RESULTS
    skip_queries = request.args.get("skip_queries") == "1"
    messages = get_flashed_messages()
    results = []    # set up empty list to store query results

    # open connection, get all the query results and pass the results and flashed status message variables
    # get the latest query only if the skip query flag is not set
    # LAST_RESULTS keeps a cache of the previous query to avoid a blank page
    if not skip_queries or not LAST_RESULTS:
        with psycopg.connect(
                dbname="studentCourses",
                user="postgres",
        ) as connection:
            with connection.cursor() as cur:
                for label, prefix, query in qd.QUERIES:
                    cur.execute(query)
                    row = cur.fetchone()
                    # handle query result which has multiple outputs on one line
                    if row and len(row) > 1:
                        value = f"GPA: {row[0]}, GRE: {row[1]}, GRE V: {row[2]}, GRE AW: {row[3]}"
                    else:
                        value = row[0] if row else None
                    results.append((label, prefix, value))
                    #print result to console
                    print(f"{label}: {prefix}{value if row else None}")
        LAST_RESULTS = results  # cache query results
    else:
        results = LAST_RESULTS
    return render_template(
        'index.html',
        results=results,
        messages=messages,
        skip_queries=skip_queries,
    )


# Connect URL route 'pull-data' to scrape, clean, save to json and load any new records into database
@app.post('/pull-data')
def pull_data():
    if pull_data_busy():
        return jsonify({"ok": False, "busy": True}), 409
    start_pull_worker()
    return jsonify({"ok": True, "busy": False}), 200


@app.post('/update-analysis')
def update_analysis():
    if pull_data_busy():
        return jsonify({"ok": False, "busy": True}), 409
    perform_update_analysis()
    return jsonify({"ok": True, "busy": False}), 200


if __name__ == "__main__":
    if "--run-pull-job" in sys.argv:
        run_pull_job()
        raise SystemExit(0)

    # load initial cleaned file into db, resetting db as a clean start
    initial_cleaned_file = "llm_extend_applicant_data.json"
    ld.load(initial_cleaned_file, reset=True)

    # Start the web application on local network
    app.run(host='0.0.0.0', port=8080, debug=True)
