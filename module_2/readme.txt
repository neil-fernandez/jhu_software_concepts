Name: Neil Fernandez (nfernan8)

Module Info: Module 2 Assignment: Web Scraping is Due on
             01/02/2026 23:59:00 EST.

Approach:
    I set up my virtual environment in venv with the dependencies using python 3.14.

    I started by incrementally building up the web scraping module in scrape.py by using concepts learned
    in class and asking questions of codex in tiny steps to build our my scraper. I checked
    robots.txt with screenshots contained in the attached pdf.

    I then built out the logic for parsing and cleaning in clean.py using the same approach and then output
    to JSON in applicant_data.json for use in the LLM. It took a lot of iteration to understand the nuances of the
    html tags and how to parse in different ways.

    The scraping, cleaning and saving of the cleaned applicant_data.json was run by directly executing main.py

    I then set up another virtual environment in venv2 with the dependencies for the llm using python 3.11.

    I tested my json applicant_data files (starting with a small file first) to understand how well the
    llm performs the additional steps in cleaning and outputting updated data fields. I made some
    modifications to the llm to help run faster and resolve some issues it was having with its
    accuracy. I then ran the llm against the 40000 records which managed to go through the first 4000
    after significant elapsed time. This output is stored in out.json.

    The llm was run using python app.py --file "../applicant_data.json" > out.json

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
   python main.py

Project Files and Descriptions:
   main.py - starts the web scraper and cleaner to output a cleaned JSON file with 40000 records.
   clean.py - contains functions clean_data and load_data which are used to perform a
              first pass of cleaning scraped data, and future load of a saved JSON file (if needed).
   scrape.py - contains functions scrape_data and save_data which are used to respectively
              perform web scraping of student data and saving the cleaned output in JSON format

   applicant_data.json - contains the generated clean.py JSON file output with 40000 records.
   applicant_data.json.jsonl - contains LLM JSON Lines output with 4799 records (run with restricted compute).
   out.json - contains the cleaned LLM JSON output with 4799 records (run with restricted compute).
   llm_extend_applicant_data.json - contains a copy of the cleaned LLM JSON output per assignment instructions.

   applicant_data_small.json - contains the generated clean.py JSON file output with 60 records (for testing).
   applicant_data_small.json.jsonl - contains LLM JSON Lines output with 60 records (for testing).
   out_small.json - contains the LLM JSON output with 60 records (for testing).

   requirements.txt - contains all the dependencies to reconstruct the environment with dependencies for main.py
                      in venv using Python 3.14.

   llm_hosting/equirements.txt - contains all the dependencies to reconstruct the llms environment with dependencies
                                 for app.py in venv2 using Python 3.11.

   robots.txt screenshot.pdf - contains the check on crawler access via the websites robots.txt


Known Bugs: N/A. There are no known bugs.

Citations: N/A.