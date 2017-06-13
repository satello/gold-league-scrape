from webapp.app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True, threaded=True, host="0.0.0.0")
