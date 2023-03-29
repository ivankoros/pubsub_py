from main import initialize_database
from main import create_webdriver
from main import click_random_deal
from main import scroll_down
import random
import time
from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def order_sub():
    driver = create_webdriver()

    # These are two different identifications for the webbrowser to think it's a different browser
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
        driver.get("https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648")

    # This sets the webdriver to undefined, so that the browser thinks it's not a webdriver
    # Again, changing identity to get past initial automation block
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    time.sleep(random.randint(2, 3))  # Sleep for a couple of seconds before doing anything, important to not get blocked

    # Location chooser
    driver.find_element(BY.XPATH, '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input').send_keys('st johns town center')
    #press enter
    driver.find_element(BY.XPATH, '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input').send_keys(u'\ue007')
    time.sleep(2)
    # click on the first element with "Choose store" in it
    driver.find_element(BY.XPATH, "//button[@aria-label=\"Choose St. John's Town Center as your store\"]").click()

    """Choosing store location
    
    This code above is needed because we initially block our location services.
    The input for choosing the location pops up automatically, so we 
    """


    build_sub_button = '//*[@id="main"]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[4]/div/div/a'
    driver.implicitly_wait(10)
    driver.find_element(BY.XPATH, build_sub_button).click()

    driver.implicitly_wait(5)
    customize_sub_button = '//*[@id="product-details-form-add-to-order"]/div[2]/div[2]/div/a/span'
    driver.find_element(BY.XPATH, customize_sub_button).click()

    driver.implicitly_wait(5)
    add_to_cart_button = '//*[@id="body-wrapper"]/div/div[2]/div/div/div[2]/button'
    driver.find_element(BY.XPATH, add_to_cart_button).click()

    # go to this link: https://www.publix.com/shop-online/in-store-pickup/checkout
    driver.get('https://www.publix.com/shop-online/in-store-pickup/checkout')

    driver.implicitly_wait(5)
    confirm_store_location_button = '//*[@id="body-wrapper"]/div/div[2]/div/div[3]/div/div/button[2]'
    driver.find_element(BY.XPATH, confirm_store_location_button).click()

    driver.implicitly_wait(5)
    checkout_button = '//*[@id="two-column-container"]/div[2]/div/div/div[1]/div[2]/button'
    driver.find_element(BY.XPATH, checkout_button).click()

    first_name_input = '//*[@name="FirstName"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, first_name_input).send_keys('John')

    last_name_input = '//*[@name="LastName"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, last_name_input).send_keys('Doe')

    phone_number_input = '//*[@name="ContactPhone"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, phone_number_input).send_keys('904-555-5555')

    email_input = '//*[@name="Email"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, email_input).send_keys('john.doe@gmail.com')

    next_button = '//*[@id="content_22"]/form/div[3]/button'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, next_button).click()

    # Define data (will be defined per request)


    # Define date picker xpath and click on it
    driver.implicitly_wait(5)
    driver.find_element(BY.CSS_SELECTOR, '.datepicker-activate').click()
    time.sleep(2)
    # Define specific date xpath and click on it
    date_of_order = "Wednesday, March 29, 2023"
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, f'//button[@aria-label="{date_of_order}"]').click()


    # Select time
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((BY.ID, "input_pickupTime93"))
    )
    dropdown.click()

    pickup_time = "2023-03-29T09:45:00"
    driver.find_element(BY.XPATH, f'//option[@value="{pickup_time}"]').click()

    next_button = '//*[@id="content_26"]/form/div[3]/div/button'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, next_button).click()

    driver.find_element(BY.XPATH, '//*[@id="content_30"]/form/div[2]/div/div[1]/div[1]').click()

    time.sleep(1000)

    driver.quit()


if __name__ == '__main__':
    order_sub()