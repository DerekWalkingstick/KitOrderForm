from website import create_app

app = create_app()

# Only run the webserver if main was ran from this file
if __name__ == '__main__':
    app.run(debug=True)