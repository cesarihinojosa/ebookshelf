from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from model import db, Book
import scrape
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables immediately after initializing the app
with app.app_context():
    db.create_all()  # Creates the tables if they don't exist

def check_goodreads():
    books = scrape.get_books() # going to goodreads to fetch data

    with app.app_context():
        # Delete all existing records from the Book table
        Book.query.delete()

        for book in books:
            new_book = Book(image=book)
            db.session.add(new_book)

        db.session.commit()

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Add a job to the scheduler to run once a day
scheduler.add_job(check_goodreads, CronTrigger(hour=0, minute=0))  # Runs daily at midnight

# Start the scheduler
scheduler.start()

# Trigger the first update immediately when the app starts
check_goodreads()  # <-- This forces the first update to happen immediately

@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except (SystemExit):
        # Shutdown the scheduler gracefully
        scheduler.shutdown()