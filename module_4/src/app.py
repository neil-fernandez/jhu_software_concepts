"""Flask application entry point for scraping, loading, and analysis views.

This module wires together route handlers for query analysis display, data
refresh operations, and background pull workflows.
"""

import load_data as ld
import query_data as qd
import scrape as sd
import subprocess
import sys
import os
import inspect

import psycopg

from flask import Flask, render_template, get_flashed_messages, request, jsonify
LAST_RESULTS = []
PULL_DATA_PROCESS = None


# check if pull data subprocess is running
def pull_data_busy():
    """Check whether the background pull-data worker is currently running.

    :return: ``True`` when the worker process is active, otherwise ``False``.
    :rtype: bool
    """
    global PULL_DATA_PROCESS
    if PULL_DATA_PROCESS is None:
        return False
    if PULL_DATA_PROCESS.poll() is None:
        return True
    PULL_DATA_PROCESS = None
    return False

# start new background process to run pull job
def start_pull_worker():
    """Start the pull-data workflow in a background subprocess."""
    global PULL_DATA_PROCESS
    PULL_DATA_PROCESS = subprocess.Popen(
        [sys.executable, __file__, "--run-pull-job"],
    )

# run pull data, calling scrape, save and looad
def run_pull_job():
    """Scrape records, write a JSON payload, and load new rows into PostgreSQL."""
    rows = sd.scrape_data(
        "https://www.thegradcafe.com/survey/",
        max_pages=5,
    )
    new_cleaned_file = "new_only.json"
    sd.save_data(rows, new_cleaned_file)
    ld.load(new_cleaned_file)

# clear cached results allowing for next request to re-run queries
def perform_update_analysis():
    """Clear cached query output so the next analysis request recomputes results."""
    global LAST_RESULTS
    # Force next /analysis load to execute fresh queries.
    LAST_RESULTS = []

# return postgresql connection
def get_db_connection():
    """Return an open PostgreSQL connection for query execution.

    Uses the ``DATABASE_URL`` environment variable when available and falls
    back to local defaults when not set.

    :return: Open PostgreSQL connection.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        connect_signature = inspect.signature(psycopg.connect)
        if "value" in connect_signature.parameters:
            return psycopg.connect(db_url)
        return psycopg.connect(conninfo=db_url)
    return psycopg.connect(
        dbname="studentCourses",
        user="postgres",
    )

# Connect URL route '/' to index.html
def index():
    """Render the analysis page with cached or freshly computed query results.

    :return: Rendered HTML response for the main analysis page.
    """
    global LAST_RESULTS
    skip_queries = request.args.get("skip_queries") == "1"
    messages = get_flashed_messages()
    results = LAST_RESULTS

    # open connection, get all the query results and pass the results and flashed status message variables
    # get the latest query only if the skip query flag is not set
    # LAST_RESULTS keeps a cache of the previous query to avoid a blank page
    if skip_queries:
        if LAST_RESULTS:
            results = LAST_RESULTS
        else:
            # Preserve page structure without hitting the database.
            results = [(label, prefix, None) for label, prefix, _query in qd.QUERIES]
    elif not LAST_RESULTS:
        with get_db_connection() as connection:
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
    return render_template(
        'index.html',
        results=results,
        messages=messages,
        skip_queries=skip_queries,
    )


# Connect URL route 'pull-data' to scrape, clean, save to json and load any new records into database
def pull_data():
    """Handle the pull-data endpoint and launch the background worker if idle.

    :return: JSON payload and HTTP status indicating launch or busy state.
    """
    if pull_data_busy():
        return jsonify({"ok": False, "busy": True}), 409
    start_pull_worker()
    return jsonify({"ok": True, "busy": False}), 200


def update_analysis():
    """Handle cache reset requests for analysis output.

    :return: JSON payload and HTTP status indicating reset or busy state.
    """
    if pull_data_busy():
        return jsonify({"ok": False, "busy": True}), 409
    perform_update_analysis()
    return jsonify({"ok": True, "busy": False}), 200

# set up Flask app using application factory pattern
def register_routes(flask_app):
    """Register all URL routes for the Flask application.

    :param flask_app: Application instance to configure.
    :type flask_app: Flask
    """
    flask_app.add_url_rule("/", endpoint="index", view_func=index, methods=["GET"])
    flask_app.add_url_rule("/analysis", endpoint="analysis", view_func=index, methods=["GET"])
    flask_app.add_url_rule("/pull-data", endpoint="pull_data", view_func=pull_data, methods=["POST"])
    flask_app.add_url_rule("/update-analysis", endpoint="update_analysis", view_func=update_analysis, methods=["POST"])

# build new Flask app
def create_app():
    """Create and configure the Flask app instance.

    :return: Configured Flask application.
    :rtype: Flask
    """
    flask_app = Flask(__name__)
    flask_app.secret_key = "dev"
    register_routes(flask_app)
    return flask_app

# keep existing global app for normal runtime; tests can call create_app() for fresh instance
app = create_app()


if __name__ == "__main__":
    if "--run-pull-job" in sys.argv:
        run_pull_job()
        raise SystemExit(0)

    # load initial cleaned file into db, resetting db as a clean start
    initial_cleaned_file = "llm_extend_applicant_data.json"
    ld.load(initial_cleaned_file, reset=True)

    # Start the web application on local network
    app.run(host='0.0.0.0', port=8080, debug=True)
