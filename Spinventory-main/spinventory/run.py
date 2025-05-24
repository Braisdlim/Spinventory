from app import create_app  # Esta línea es crucial

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)