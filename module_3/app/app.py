"""
This Python script is used to start a local web application
built using Flask to display query data, scrape and load new records
into a postgresql database and update query analysis as required.
"""

import load_data as ld
import query_data as qd
import scrape as sd

import psycopg

from flask import Flask, render_template, url_for, redirect, flash, get_flashed_messages, request

app = Flask(__name__)   # Create Flask app instance
app.secret_key = "dev"  # secret key to flash message
LAST_RESULTS = []

# Connect URL route '/' to index.html
@app.route('/')
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
    # scrape data from grad cafe up to max_pages
    rows = sd.scrape_data(
        "https://www.thegradcafe.com/survey/",
        max_pages=5,
    )

    # save data to new_only.json
    new_cleaned_file = "new_only.json"
    sd.save_data(rows, new_cleaned_file)

    # load saved data into database
    ld.load(new_cleaned_file)

    # set flashed status message for redirect
    status = f"Pulled {len(rows)} new entries into database, also saved in {new_cleaned_file}."
    flash(status)

    #return redirect
    return redirect(url_for("index", skip_queries=1))


if __name__ == "__main__":

    # load initial cleaned file into db, resetting db as a clean start
    initial_cleaned_file = "llm_extend_applicant_data.json"
    ld.load(initial_cleaned_file, reset=True)

    # Start the web application on local network
    app.run(host='0.0.0.0', port=8080, debug=True)
