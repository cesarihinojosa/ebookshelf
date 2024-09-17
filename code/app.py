from flask import Flask, render_template
import scrape

app = Flask(__name__)

@app.route('/')
def home():
    books = scrape.get_books()
    return render_template('index.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)