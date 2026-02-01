Name: Neil Fernandez (nfernan8)

Module Info: Module 2 Assignment: Web Scraping is Due on
             01/02/2026 23:59:00 EST.

Approach:
    I started by incrementally building up the web scraping module by using concepts learned
    in class and asking questions of codex in tiny steps to build our my scraper. I checked
    robots.txt with screenshots contained in the attached pdf.

    I then built out the logic for parsing and cleaning using the same method and then output
    to JSON for use in the LLM. It took a lot of iteration to understand the nuances of the
    html tags and how to parse in different ways.

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
              first pass of cleaning scraped data and loading the saved JSON file.
   scrape.py - contains functions scrape_data and save_data which are used to respectively
              perform web scraping of student data and saving the cleaned output in JSON format
   applicant_data.json - contains the generated JSON file.
   requirements.txt - contains all the dependencies to reconstruct the environment

Known Bugs: N/A. There are no known bugs.

Citations: N/A.