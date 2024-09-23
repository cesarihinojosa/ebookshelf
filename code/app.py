from flask import Flask, render_template
from sqlalchemy import func
from model import db, Book
import scrape
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

logging.basicConfig(
    level=logging.INFO,  # Set the lowest level of messages to log (DEBUG and above)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Custom format for log messages
    filename='logs/ebookshelf.log',  # Log messages to this file (omit this argument to log to console)
    filemode='a'  # 'w' for overwriting the log file, 'a' for appending
)

# Create tables immediately after initializing the app
with app.app_context():
    db.create_all()  # Creates the tables if they don't exist

def check_goodreads():
    books = scrape.get_books() # going to goodreads to fetch data

    with app.app_context():
        # Delete all existing records from the Book table
        Book.query.delete()
        logging.info("Deleted all previous records, resetting database...")

        for book in books:
            new_book = Book(image=book)
            db.session.add(new_book)

        db.session.commit()
        book_count = db.session.query(func.count(Book.id)).scalar()
        logging.info(f"Finished resetting and there are {book_count} books in the database")

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Add a job to the scheduler to run once a day
logging.info("Scheduler is set to run every Monday at 11am with 120 seconds of jitter")
scheduler.add_job(check_goodreads, 'cron', day_of_week='mon', hour=11, minute=0, jitter=120)  # Runs daily at midnight

# Start the scheduler
scheduler.start()

@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler gracefully
        scheduler.shutdown()