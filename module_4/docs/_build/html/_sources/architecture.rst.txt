Architecture
============

Layered Responsibilities
------------------------

Web Layer (Flask)
-----------------

Implemented in ``module_4/src/app.py``.

Responsibilities:

1. Exposes routes:
   ``/``, ``/analysis``, ``/pull-data``, ``/update-analysis``.
2. Coordinates pull and refresh operations.
3. Executes query rendering for the analysis page.
4. Maintains lightweight in-process state:
   ``LAST_RESULTS`` and ``PULL_DATA_PROCESS``.

ETL Layer
---------

Implemented across ``scrape.py``, ``clean.py``, and ``load_data.py``.

Responsibilities:

1. ``scrape.py``: Collects raw records from web pages and filters against known URLs.
2. ``clean.py``: Normalizes and validates data fields.
3. ``load_data.py``: Creates/inserts records into PostgreSQL and enforces uniqueness rules.

Database Layer
--------------

Implemented through ``psycopg`` calls in ``app.py``, ``load_data.py``, and ``query_data.py``.

Responsibilities:

1. Stores applicant records in PostgreSQL.
2. Serves SQL-based analytics defined in ``query_data.py``.
3. Supplies values rendered on the analysis page.

Data Flow
---------

1. Client calls ``POST /pull-data``.
2. App starts background pull worker.
3. Worker runs scrape -> save -> load.
4. Client calls ``POST /update-analysis`` to clear cached results.
5. Client requests ``GET /analysis`` to render fresh SQL outputs.

