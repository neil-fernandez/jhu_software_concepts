Name: Neil Fernandez (nfernan8)

Module Info: Module 4 Assignment: Database Queries

Approach:
    I set up my environment in module_4/venv using Python 3.14 and installed all dependencies
    from requirements.txt.

    I wrote a range of unit tests per the assignment requirements and an integration test which
    I continuously tested using pytest. I added pytest markers to all of my tests and checked
    the Policy that no test should be unmarked using pytest -m "web or buttons or analysis or db or integration".
    I then used use pytest-cov to guarantee 100% coverage of all code and if not covered I created
    unit tests to close the gap and produce a coverage summary.

    I created a simple CI pipeline using GitHub actions and tested it sucessfully putting the result
    in actions_success.png. My workflow file was stored in test.yml

    I also generated Sphinx documentation for setup, architecture, API references, testing guide,
    and operational notes, with HTML build/publish configuration for GitHub and Read the Docs.

Instructions:
1. Clone the GitHub repo
   git clone git@github.com:neil-fernandez/jhu_software_concepts.git
   cd jhu_software_concepts/module_4

2. Create a virtual environment
   python -m venv venv

3. Activate virtual environment (PowerShell)
   .\venv\Scripts\Activate.ps1

4. Install dependencies
   python -m pip install --upgrade pip
   pip install -r requirements.txt

5. Set database environment variable (recommended)
   $env:DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:5432/studentCourses"

6. Run tests
   pytest

7. Run main application
   cd src
   python app.py

8. Build Sphinx docs HTML
   cd ..
   sphinx-build -b html docs/source docs/_build/html

Project Files and Descriptions:
   src/app.py - starts the Flask app, wires routes, manages busy-state, and renders SQL analysis output.
   src/load_data.py - loads JSON data into PostgreSQL, cleans text/numbers, creates schema/index,
                      and applies URL-based dedupe on insert.
   src/query_data.py - defines SQL query statements and labels used for analysis rendering.
   src/scrape.py - scrapes Grad Cafe rows, compares against existing URLs, and saves new cleaned records.
   src/clean.py - normalizes and cleans scraped input fields.

   src/llm_extend_applicant_data.json - initial cleaned LLM dataset used for base load.
   src/new_only.json - new scraped/cleaned records staged for load.

   src/templates/base.html - base layout template.
   src/templates/index.html - analysis page with query output and control buttons.
   src/static/main.css - stylesheet for app UI.

   tests/ - pytest suite for web routes, buttons, DB behavior, formatting, and end-to-end flows.
   docs/source/ - Sphinx documentation source files.
   .readthedocs.yaml - Read the Docs build configuration.
   requirements.txt - project dependencies for app, tests, and docs.

Known Bugs: N/A. There are no known bugs at this time.

Citations: N/A.
