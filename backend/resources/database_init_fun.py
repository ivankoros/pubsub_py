from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQSQLAlchemy configuration & setup
Base = declarative_base()


# Create a class for the SQAlchemy table that will be created, making it easy to add name and date of subs on sale
class SubDeal(Base):
    __tablename__ = 'sub_deals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    date = Column(DateTime)
    location = Column(String(255))

    def __init__(self, name, date, location):
        self.name = name
        self.date = date
        self.location = location


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(255))
    name = Column(String(255))
    selected_store = Column(JSON)
    state = Column(String(45),
                   default='start')
    nearest_stores = Column(JSON)

    def __init__(self, phone_number, name, state):
        self.phone_number = phone_number
        self.name = name
        self.selected_store = None
        self.state = state
        self.nearest_stores = None


def initialize_database():
    """Initialize MySQL database

    I'm using a mysql database to store the sub deals over previously using a sqlite database.
    I'm doing this because SQLite doesn't support datetime comparisons, meaning I cant compare a newly found
    sub deal to a previously found sub deal to see if it's the same sub deal.

    I'm also using MySQL because I'll be able to host it on a server much easier with the major cloud providers like AWS and GCP.
    This way, I can run the bot away from my computer and have it dockerized, so it can run on any machine.

    Edit: Looking back at it now, SQLite could've been used to compare time like this:

        from sqlalchemy import func
        table_db = session.query.filter(func.DATE(SubDeal.date == today)

    However, I am staying with, and still prefer MySQL, for the scalability and access.

    :return:
        Session: The database session object for the database
    """
    load_dotenv(override=True, dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", 'config\\.env')))

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"

    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    return session
