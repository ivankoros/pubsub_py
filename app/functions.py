from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime
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

    def __init__(self, name, date):
        self.name = name
        self.date = date

    def __repr__(self):
        return f"Sub: {self.name} Sale date: {self.date}"

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
    load_dotenv(override=True, dotenv_path="../config/.env")

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"

    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()

    return session


def create_webdriver():
    """Create a selenium webdriver for the bot to use

    Returns:
        webdriver: The selenium webdriver
    """
    # Selenium runtime options
    options = Options()
    options.add_argument("--incognito")
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.set_capability("acceptInsecureCerts", True)
    options.set_capability("acceptSslCerts", True)
    options.set_capability("unhandledPromptBehavior", "accept")
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_experimental_option("prefs", prefs)
    # one of the accept terms paths: /html/body/div[1]/div/div/div[3]/div/div/button
    """ Add options to selenium runtime
        --headless: Run without opening a window
        --disable-blink-features=AutomationControlled: Disable the "Chrome is being controlled by automated test software" message
        --incognito: Run in incognito mode
        Exclude switches and useAutomationExtension both remove identifiers for selenium being used as an automated test, which chrome doesnt like

        The options are added to the webdriver.Chrome() function which is passed to the webdriver and executed

    """

    # Download the latest chromium webdriver to mimic Chrome browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver


if __name__ == "__main__":
    pass
