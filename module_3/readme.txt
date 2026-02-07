Name: Neil Fernandez (nfernan8)

Module Info: Module 3 Assignment: Database Queries is Due on
             08/02/2026 23:59:00 EST.

Approach:


Instructions:
1. Clone the Github repo
   git clone git@github.com:neil-fernandez/jhu_software_concepts.git cd jhu_software_concepts

2. Create a virtual environment for the dependencies from requirements.txt
   python -m venv venv

3. Activate virtual environment
   .\venv\Scripts\activate

4. Install the dependencies
   python -m pip install requirements.txt

5. Run main application
   python app.py

Project Files and Descriptions:
   app.py - starts the web scraper and cleaner to output a cleaned JSON file with 40000 records.
   load_data.py - contains functions clean_data and load_data which are used to perform a
              first pass of cleaning scraped data, and future load of a saved JSON file (if needed).
   query_data.py - contains functions scrape_data and save_data which are used to respectively
              perform web scraping of student data and saving the cleaned output in JSON format
   llm_extend_applicant_data.json - contains a copy of the cleaned LLM JSON output per assignment instructions.

   requirements.txt - contains all the dependencies to reconstruct the environment with dependencies for app.py
                      in venv using Python 3.14.


Known Bugs: N/A. There are no known bugs.

Citations: N/A.