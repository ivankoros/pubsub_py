# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import random
from selenium.webdriver.support.wait import WebDriverWait
import re
from dotenv import load_dotenv
from datetime import datetime, date
import os

# SQSQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, DateTime, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import cast, Date

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


engine = create_engine('sqlite:///sub_deal_data.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Load environment variables
load_dotenv()


# Selenium runtime options
options = Options()
# options.add_argument("--incognito")
options.add_argument("--headless=new")
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

publix_sub_link = "https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648"  # Publix deli subs link

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # Also removes the "Chrome is being controlled by automated test software" message

""" Humanize the bot

The following code is used to make the bot appear more human-like. 
I heavily use the random library to pick random values for the bot to use to wait and click on elements.

This is extremely important. If not used, Selenium is detected and the link will re-direct to a page that says no subs exist.

Examples:
It will wait between 2 and 5 seconds before doing anything, and will scroll down the page to make it look like the user is actually looking at the page. 
It randomly click on an element to make it look like the user is clicking on a deal.


"""
# Go to link, wait between 2 and 5 seconds to do anything
driver.get(publix_sub_link)
time.sleep(random.randint(2, 5))

# Wait 3 seconds, then find all elements with the classname matching the one that sale deals are in
wait = WebDriverWait(driver, 3)
saving_elements_by_class = driver.find_elements(By.CLASS_NAME,
                                                "p-text.paragraph-sm.strong.context--default.color--null")

# Wait between 2 and 5 seconds, then scroll down the page
time.sleep(random.randint(2, 5))
driver.execute_script('window.scrollTo(0, 700)')

# Print the number of elements found by class name
print(str(len(saving_elements_by_class)) + " elements found by class name")

# Filter found deals by seeing if they contain the word same.
# A lot of elements found are not deals (just have same classname), so I filter them out
deals = []
for each in saving_elements_by_class:
    if "Save" in each.text:
        deals.append(each)

# Sleep between 2 and 5 seconds, then scroll down the page
time.sleep(random.randint(2, 5))
driver.execute_script('window.scrollTo(0, 1400)')

# execute script to click on the element
driver.execute_script("arguments[0].click();", deals[random.randint(0, len(deals) - 1)])

# Find the name of the sub on sale by looking through the filtered element's parent text
subs_on_sale = []
pattern = r"(.*Sub)"  # This is the regex pattern used below to get the name of the sub

def find_sub_parent(element):
    """Find the sub name of the element that contains the word "Save"

    Recursively look up the parent element until the word "Sub" is found
    It comes out messy like: "Publix Italian Sub\nGenoa Salami, Tavern Ham, Hot Cappy Ham, Choice of Cheese and Salad..."
    So I use regex to get all the words before the word "Sub" which is the name of the sub: "Publix Italian Sub"
    Then I append it to the list

    :param element: the list of elements that contain the word "Save"
    :return: the list of subs on sale: "Publix Italian Sub"
    """

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


# Loop through the list of elements that contain the word "Save" call the find_sub_parent function on each element
for item in deals:
    find_sub_parent(item)

driver.quit()
