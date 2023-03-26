import random
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQSQLAlchemy configuration & setup
Base = declarative_base()

# Create a class for the SQAlchemy table that will be created, making it easy to add name and date of subs on sale
class SubDeal(Base):
    __tablename__ = 'sub_deals'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    date = Column(DateTime)

    def __init__(self, name, date):
        self.name = name
        self.date = date

    def __repr__(self):
        return f"Sub: {self.name} Sale date: {self.date}"


def create_webdriver():
    """Create a selenium webdriver for the bot to use

    Returns:
        webdriver: The selenium webdriver
    """
    # Selenium runtime options
    options = Options()
    # options.add_argument("--incognito")
    #options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

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

def find_saving_elements(driver):
    WebDriverWait(driver, 3)
    return driver.find_elements(By.CLASS_NAME, "p-text.paragraph-sm.strong.context--default.color--null")

def scroll_down(driver):
    time.sleep(random.randint(2, 5))
    driver.execute_script(f'window.scrollTo(0, {random.randint(700, 1400)})')

def click_random_deal(driver, deals):
    time.sleep(random.randint(2, 5))
    driver.execute_script("arguments[0].click();", deals[random.randint(0, len(deals) - 1)])


""" Humanize the bot

The following code is used to make the bot appear more human-like. 
I heavily use the random library to pick random values for the bot to use to wait and click on elements.

This is extremely important. If not used, Selenium is detected and the link will re-direct to a page that says no subs exist.

Examples:
It will wait between 2 and 5 seconds before doing anything, and will scroll down the page to make it look like the user is actually looking at the page. 
It randomly click on an element to make it look like the user is clicking on a deal.


"""

def find_sub_parent(element, session):
    """Find the sub name of the element that contains the word "Save"

    Recursively look up the parent element until the word "Sub" is found
    It comes out messy like: "Publix Italian Sub\nGenoa Salami, Tavern Ham, Hot Cappy Ham, Choice of Cheese and Salad..."
    So I use regex to get all the words before the word "Sub" which is the name of the sub: "Publix Italian Sub"
    Then I append it to the list

    :param session: the database session
    :param element: the list of elements that contain the word "Save"
    :return: the list of subs on sale: "Publix Italian Sub"
    """
    pattern = r"(.*Sub)"

    while element is not None:
        parent = element.find_element(By.XPATH, '..')
        if "Sub" in parent.text:
            match = re.search(pattern, parent.text)
            sub_name = match.group(1)

            datetime_obj = datetime.now()
            today = datetime_obj.date()  # Get the current date (year-month-day)

            # If the same sub is on sale on the same date, don't add it to the database
            existing_deal = session.query(SubDeal).filter(
                SubDeal.name == sub_name,
                SubDeal.date == today
                ).first()

            if not existing_deal:
                deal = SubDeal(sub_name, today)
                session.add(deal)
                session.commit()
                print(f"The {sub_name.lower()} is on sale!")
            else:
                print(f"The {sub_name.lower()} is a duplicate!")

            return
        element = parent


def main():

    load_dotenv()

    # Create the database
    engine = create_engine('sqlite:///sub_deal_data.db', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the webdriver
    driver = create_webdriver()

    # Get the link to the subs page and go to the webpage
    publix_sub_link = "https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648"
    driver.get(publix_sub_link)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    time.sleep(random.randint(2, 5))
    scroll_down(driver)

    # Find all the elements that contain the word "Save"
    saving_elements_by_class = find_saving_elements(driver)
    print(str(len(saving_elements_by_class)) + " elements found by class name")

    # Filter the list to only include elements that contain the word "Save"
    deals = [each for each in saving_elements_by_class if "Save" in each.text]

    click_random_deal(driver, deals)

    for item in deals:
        find_sub_parent(item, session)

    driver.quit()


if __name__ == '__main__':
    main()
