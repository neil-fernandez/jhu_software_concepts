Operational Notes
=================

Busy-State Policy
-----------------

The app uses a single in-process busy flag through ``PULL_DATA_PROCESS`` in
``module_4/src/app.py``.

Policy:

1. ``POST /pull-data`` returns ``409`` with ``{"busy": true}`` if a pull job is already running.
2. ``POST /update-analysis`` also returns ``409`` while pull is in progress.
3. ``pull_data_busy()`` clears stale process state once the worker exits.

This prevents overlapping ETL runs and keeps update operations consistent.

Idempotency Strategy
--------------------

Idempotency is enforced at database write time in ``module_4/src/load_data.py``.

Key mechanisms:

1. ``CREATE UNIQUE INDEX IF NOT EXISTS applicantdata_url_key ON applicantData (url)``
2. ``INSERT ... ON CONFLICT (url) DO NOTHING``

Result:

Repeated pull/load operations do not duplicate rows for previously seen URLs.

Uniqueness Keys
---------------

Current key choices:

1. ``p_id`` is primary key.
2. ``url`` is the operational dedupe key used for idempotent ingestion.

Design implication:

If the same application appears again with identical URL, it is skipped.

Troubleshooting (Local and CI)
------------------------------

``psycopg.errors.UndefinedTable: relation "applicantdata" does not exist``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. Analysis routes are queried before data/table initialization in a test path.

Checks/fixes:

1. Ensure app startup path calls ``ld.load(..., reset=True)`` when intended.
2. In route tests that only validate page shell, use ``skip_queries=1``.
3. Confirm tests are running against current committed ``module_4/src/app.py``.

``TypeError ... lambda() takes 0 positional arguments but 1 was given``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. Test double for ``psycopg.connect`` only accepts keyword args.

Checks/fixes:

1. Keep ``get_db_connection()`` compatible with both positional and keyword-only doubles.
2. Re-run failing test locally before pushing:
   ``pytest tests/test_app.py tests/test_integration_end_to_end.py -q``

Coverage drops below 100% in local runs but passes in CI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. Different runtime environment/branches exercised locally vs CI.

Checks/fixes:

1. Match CI env vars locally, especially ``DATABASE_URL``.
2. Run from ``module_4`` so ``pytest.ini`` options and paths are applied.

``pytest: error: unrecognized arguments: --cov ...``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. Running pytest outside the project virtualenv or without ``pytest-cov``.

Checks/fixes:

1. Use ``module_4/venv`` pytest binary, or install project requirements first.

Sphinx build fails with missing extension import
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. ``conf.py`` references an extension not installed in environment.

Checks/fixes:

1. Install dependencies from ``module_4/requirements.txt``.
2. Keep ``module_4/docs/source/conf.py`` extensions aligned with installed packages.

GitHub Actions fails but local passes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cause:

1. CI ran an older commit or different files than local working tree.

Checks/fixes:

1. Confirm required files are committed and pushed:
   ``module_4/src/app.py``, workflow files, and docs files.
2. Verify the failing run commit SHA matches your intended commit.

