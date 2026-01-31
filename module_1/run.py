from app import create_app

if __name__=='__main__':
    # Run the application
    my_webapp = create_app()
    my_webapp.run(host='0.0.0.0', port=8080, debug=True)
