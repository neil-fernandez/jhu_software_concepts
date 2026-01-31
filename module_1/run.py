"""
This Python script is used to start a local web application for my
personal web application which is built using Flask.
"""
from app import create_app  # Import object of Flask class

if __name__=='__main__':
    my_webapp = create_app()    # Run the function using an application factory

    my_webapp.run(host='0.0.0.0', port=8080, debug=True)    # Start the web application on local network
