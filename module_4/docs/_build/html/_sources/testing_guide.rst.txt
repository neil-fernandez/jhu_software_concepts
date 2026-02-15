Testing Guide
=============

Run the Full Suite
------------------

From ``module_4``:

.. code-block:: bash

   pytest

Run by Marker
-------------

Markers defined in ``module_4/pytest.ini``:

1. ``web``
2. ``buttons``
3. ``analysis``
4. ``db``
5. ``integration``

Examples:

.. code-block:: bash

   pytest -m web
   pytest -m buttons
   pytest -m "integration and not db"

Expected Selectors and Route Targets
------------------------------------

UI and route checks asserted by tests include:

1. Route methods:
   ``GET /analysis``, ``POST /pull-data``, ``POST /update-analysis``
2. Button DOM ids:
   ``pull-data-button`` and ``update-analysis-button``
3. Required test ids:
   ``data-testid="pull-data-btn"`` and ``data-testid="update-analysis-btn"``

Common Fixtures
---------------

Frequently used fixtures:

1. ``app`` fixture creates a fresh Flask app via ``create_app()``.
2. ``client`` fixture provides Flask ``test_client()`` for HTTP route tests.

Test Doubles and Monkeypatch Patterns
-------------------------------------

The tests use monkeypatch-based doubles extensively. Common replacements:

1. ETL functions:
   ``sd.scrape_data``, ``sd.save_data``, ``ld.load``
2. Process handling:
   ``subprocess.Popen`` to run synchronously in tests
3. Database connection:
   ``psycopg.connect`` replaced by fake connection/cursor objects
4. Rendering and route internals:
   ``render_template``, ``get_db_connection``, ``pull_data_busy``

Representative files:

1. ``module_4/tests/test_app.py``
2. ``module_4/tests/test_buttons.py``
3. ``module_4/tests/test_integration_end_to_end.py``

