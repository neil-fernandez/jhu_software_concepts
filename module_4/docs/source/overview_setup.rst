Overview and Setup
==================

Application Overview
--------------------

This project is a Flask web app backed by PostgreSQL. It:

1. Scrapes application records from The Grad Cafe.
2. Cleans and normalizes the records.
3. Loads deduplicated records into the database.
4. Renders SQL analysis results through web routes.

Repository Paths Used by the App
--------------------------------

1. App entrypoint: ``module_4/src/app.py``
2. Tests: ``module_4/tests``
3. Sphinx docs source: ``module_4/docs/source``

Environment Variables
---------------------

The app supports the following database configuration:

1. ``DATABASE_URL`` (preferred), for example:
   ``postgresql://postgres:postgres@127.0.0.1:5432/studentCourses``
2. Fallback if ``DATABASE_URL`` is unset:
   ``dbname=studentCourses`` and ``user=postgres``

Run the Application
-------------------

From ``module_4/src``:

.. code-block:: bash

   python app.py

App behavior at startup:

1. Loads ``llm_extend_applicant_data.json`` with reset enabled.
2. Starts Flask at ``0.0.0.0:8080``.

Run Tests
---------

From ``module_4``:

.. code-block:: bash

   pytest

To mirror CI database settings:

.. code-block:: bash

   export DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:5432/studentCourses"
   pytest

