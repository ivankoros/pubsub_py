import random
import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.orm import declarative_base
from backend.selenium_app.helpers import webdriver_location_input

from backend.resources import SubDeal
from backend.resources import create_webdriver
from backend.resources import initialize_database

# SQSQLAlchemy configuration & setup
Base = declarative_base()


def find_saving_elements(driver):
    time.sleep(
        10)  # An implicit wait cannot be used here because the page is dynamically loaded and the elements change as the page loads
    sale_elements = driver.find_elements(By.CLASS_NAME, "p-text.paragraph-sm.strong.context--default.color--null")

    return sale_elements


""" Humanize the bot

The following code is used to make the bot appear more human-like. 
I heavily use the random library to pick random values for the bot to use to wait and click on elements.

This is extremely important. If not used, Selenium is detected and the link will re-direct to a page that says no subs exist.

Examples:
It will wait between 2 and 5 seconds before doing anything, and will scroll down the page to make it look like the user is actually looking at the page. 
It randomly click on an element to make it look like the user is clicking on a deal.


"""

def find_sub_parent(element, session, location):
    """Find the sub name of the element that contains the word "Save"

    Recursively look up the HTML parent element of the sale items until the word "Sub" is found
    It comes out messy like: "Publix Italian Sub\nGenoa Salami, Tavern Ham, Hot Cappy Ham, Choice of Cheese and Salad..."
    So I use regex to get all the words before the word "Sub" which is the name of the sub: "Publix Italian Sub"
    Then I append it to the list

    :param session: the database session
    :param element: the list of elements that contain the word "Save"
    :param location: the location of the store: "St. Johns Town Center"
    :return: the list of subs on sale: "Publix Italian Sub"
    """

    pattern = r"(.*Sub)"
    today = datetime.now().date()

    while element is not None:
        parent = element.find_element(By.XPATH, '..')
        if "Sub" in parent.text:
            match = re.search(pattern, parent.text)  # Get the name of the sub: "Publix Italian Sub"
            sub_name = match.group(1)

            # Query the database to see if the sub is already in the database at the same date as today
            existing_deal = session.query(SubDeal).filter(
                SubDeal.name == sub_name,
                SubDeal.date == today
                ).first()

            # If the same sub is on sale on the same date, don't add it to the database
            if not existing_deal:
                deal = SubDeal(sub_name, today, location)
                session.add(deal)
                session.commit()
                print(f"The {sub_name.lower()} is newly on sale, adding to database!")
            else:
                print(f"The {sub_name.lower()} is a duplicate sale, not adding!")

            return
        element = parent


def main():

    # Create the database
    session = initialize_database()

    # Create the webdriver
    driver = create_webdriver()

    user_agent_array = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]

    # This reloads the page with per user agent
    # This is extremely important, many times, the first or even second user agent will be blocked (randomly),
    # so they're needed to change the identity of the browser to successfully load in the page (the hardest part)

    for i in range(len(user_agent_array)):
        # Setting user agent iteratively as Chrome 108 and 107
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent_array[i]})
        print(driver.execute_script("return navigator.userAgent;"))
        driver.get("https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648?facet=onSale%3A%3Atrue")

    # Get the link to the subs page and go to the webpage
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    time.sleep(random.randint(2, 5))

    try:
        accept_button = driver.find_element(By.XPATH,
                                            '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]')
        wait = WebDriverWait(driver, 3)
        if wait.until(EC.element_to_be_clickable((By.XPATH,
                                                  '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]'))):
            accept_button.click()
    except:
        pass

    location = 'St. John\'s Town Center'
    webdriver_location_input(driver, location)

    # Find all the elements that contain the word "Save"
    saving_elements_by_class = find_saving_elements(driver)
    print(str(len(saving_elements_by_class)) + " elements found by class name")

    # Filter the list to only include elements that contain the word "Save"
    deals = [each for each in saving_elements_by_class if "Save" in each.text]

    for item in deals:
        find_sub_parent(item, session, location)

    driver.quit()


if __name__ == '__main__':
    main()
