Name: Neil Fernandez (nfernan8)

Module Info: Module 1 Assignment: Personal Web Application is Due on
             01/02/2026 23:59:00 EST.

Instructions

1. Clone the Github repo
   git clone git@github.com:neil-fernandez/jhu_software_concepts.git cd jhu_software_concepts

2. Create a virtual environment for the dependencies from requirements.txt
   python -m venv venv

3. Activate virtual environment
   .\venv\Scripts\activate

4. Install the dependencies
   python -m pip install requirements.txt

5. Run web application
   python run.py

Project files and descriptions

   run.py - starts a local web application for my personal web application which is built using Flask.

   __init__.py - configures a Flask application which contains URL routes within a 'views' blueprint.

   views.py - declare three URL routes to web pages (templates) in a 'views' blueprint.

   views.py - declares three URL routes to web pages (templates) in a 'views' blueprint.

   base.html - is the main layout parent template for the web application with head and body.

   home.html, contact.html, projects.html - contain the child templates (views) to render in base.

   requirements.txt - contains all the dependencies to reconstruct the environment

How I completed the project

I started with a very basic Flask web app in a single python script 'run.py'. I then moved part of the
code to '__init__.py' and created the standardised Flask folder structure for reusability.
I then created 'templates' folder for my base.html template and page views (child html templates).
I then created 'views.py' to contain my blueprint with URL routes to my child templates.
The final step was to upload an image and style my web app using css. I checked my html and css
using an LLM to ensure validity and functionality as cited below.

Known Bugs: N/A. There are no known bugs.

Citations: Real Python (2024). Built a Scalable Flask Web Project From Scratch.
           https://realpython.com/flask-project/#add-dependencies
           OpenAI. (2026). ChatGPT (5.2).
           https://chat.openai.com/chat.