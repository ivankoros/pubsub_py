from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random

def webdriver_location_input(driver, location):
    """Choosing store location

    This code above is needed because we initially block our location services.
    The input for choosing the location pops up automatically, so we click on the text box, enter an address, and press enter.
    The store elements are easy to locate because each has their own unique labels (e.g. "Choose St. John's Town Center as your store").
    So, we use the address variable to find the correct store, wait for it to load, and then click on it. This exits the address prompt.

    """
    location_selection_textbox_path = '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input'

    driver.find_element(By.XPATH, location_selection_textbox_path).send_keys(location)
    driver.find_element(By.XPATH, location_selection_textbox_path).send_keys(u'\ue007')  # Press enter

    location_address = f'//button[@aria-label="Choose {location} as your store"]'

    correct_store_choose_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, location_address))
    )

    store_element = correct_store_choose_option.find_element(By.XPATH, './ancestor::li')

    # Find the header element within the store element using XPath
    header_element = store_element.find_element(By.CSS_SELECTOR, '.store-info .title-wrapper h3')

    correct_store_choose_option.click()

    official_location_name = header_element.text

    return official_location_name
