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
import os

load_dotenv()

options = Options()
options.add_experimental_option("detach", True)
# options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

publix_sub_link = "https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648"

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Go to link, wait between 2 and 5 seconds to do anything
driver.get(publix_sub_link)
time.sleep(random.randint(2, 5))

# Wait 3 seconds, find elements on class, then randomly click somewhere on the page
wait = WebDriverWait(driver, 3)
saving_elements_by_class = driver.find_elements(By.CLASS_NAME,
                                                "p-text.paragraph-sm.strong.context--default.color--null")

# Sleep between 2 and 5 seconds, then scroll down the page
time.sleep(random.randint(2, 5))
driver.execute_script('window.scrollTo(0, 700)')

# Print the number of elements found by class name then filter them if they contain the word "Save"
print(str(len(saving_elements_by_class)) + " elements found by class name")

deals = []
for each in saving_elements_by_class:
    if "Save" in each.text:
        deals.append(each)

# Sleep between 2 and 5 seconds, then scroll down the page
time.sleep(random.randint(2, 5))
driver.execute_script('window.scrollTo(0, 1400)')

# execute script to click on the element
driver.execute_script("arguments[0].click();", deals[random.randint(0, len(deals) - 1)])


# Find subs on sale function from parent elements
subs_on_sale = []
pattern = r"(.*Sub)"
def find_sub_parent(element):
    """Find the sub name of the element that contains the word "Save"

    Recursively look up the parent element until the word "Sub" is found
    It comes out messy like: "Publix Italian Sub\nGenoa Salami, Tavern Ham, Hot Cappy Ham, Choice of Cheese and Salad..."
    So I use regex to get the first word before the word "Sub" which is the name of the sub: "Publix Italian Sub"
    Then I append it to the list

    :param element: the list of elements that contain the word "Save"
    :return: the list of subs on sale: "Publix Italian Sub"
    """
    while element is not None:
        parent = element.find_element(By.XPATH, '..')
        if "Sub" in parent.text:
            match = re.search(pattern, parent.text)
            subs_on_sale.append(match.group(1))
            return subs_on_sale
        element = parent
    return subs_on_sale


for index, item in enumerate(deals):
    find_sub_parent(item)
    print("The " + subs_on_sale[index].lower() + " is on sale!")

driver.quit()
