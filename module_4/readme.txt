Name: Neil Fernandez (nfernan8)

Module Info: Module 4 Assignment: Database Queries is Due on
             15/02/2026 23:59:00 EST.

Approach:
    I set up my virtual environment in venv with the dependencies using python 3.14.

    I started by building out my load_data.py module to take the cleaned llm data input and load it into
    my postgresql database. I used the assignment schema and included handlers for the data types.

    I then built out query_data to implement the query requirements from the assignment. I tested the output
    multiple times to ensure it was calculating correctly. I also implemented my own queries.

    I then built out my flask app in app.py. I brought across my work from module 2 in clean.py and scrape.py
    to address part A and part B of the flask webpage part of the assignment. I styled my site per the
    assignment instructions. I then implemented the buttons which made use of my clean, scrape, load and query
    modules. I used some javascript to prevent users from updating analysis while pulling data.

    In the final product, the app was tested and run by directly executing app.py

Instructions:
1. Clone the Github repo
   git clone git@github.com:neil-fernandez/jhu_software_concepts.git cd jhu_software_concepts

2. Create a virtual environment for the dependencies from requirements.txt
   python -m venv venv

3. Activate virtual environment
   .\venv\Scripts\activate

4. Install the dependencies
   python -m pip install requirements.txt

5. Run main application *************
   python app.py **************

Project Files and Descriptions:
   app.py - starts the flask app to load the llm output into the database and display query results in index.html
   load_data.py - contains functions to load a json file into the database schema (load),
                  clean null bytes (clean_text), and parse floats to enable load using the correct
                  data type (parse_number).
   query_data.py - contains declarations for all the sql queries, the structured output to render on the website
                   and to output to console, and it contains a main declaration to run the script directly for
                   testing purposes.
   scrape.py - contains functions to respectively perform web scraping of student data (scrape_data),
               compare the scraped data against a normalised list of urls from the existing applicant database
               (get_existing_urls and normalise_url), and save the new cleaned records in JSON format and back
               to the database (save_data).
   clean.py - contains functions clean_data which is used to clean scraped data using regex, beautifulsoup and
              string expressions.

   llm_extend_applicant_data.json - contains a copy of the cleaned LLM JSON output per assignment instructions.
   new_only.json - contains a copy of the newly scraped/cleaned data from grad cafe.

   base.html - is the main layout parent template for the web application with head and body.
   index.html - is the rendered html template which contains the user instructions, query output, and
                buttons to pull more scraped/cleaned data loaded into the database and to update analysis
                for the database queries.
   main.css - contains all the website styling used.

   requirements.txt - contains all the dependencies to reconstruct the environment with dependencies for app.py
                      in venv using Python 3.14.

Known Bugs: N/A. There are no known bugs.

Citations: N/A.