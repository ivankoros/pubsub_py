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
    useragentarray = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]

    for i in range(len(useragentarray)):
        # Setting user agent iteratively as Chrome 108 and 107
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[i]})
        print(driver.execute_script("return navigator.userAgent;"))
        driver.get("https://www.publix.com/c/subs-and-more/33957951-95fa-4408-b54a-dd570a7e8648")

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    time.sleep(random.randint(2, 3))
    driver.find_element(BY.XPATH, '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input').send_keys('st johns town center')
    #press enter
    driver.find_element(BY.XPATH, '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input').send_keys(u'\ue007')
    time.sleep(2)
    # click on the first element with "Choose store" in it
    driver.find_element(BY.XPATH, "//button[@aria-label=\"Choose St. John's Town Center as your store\"]").click()

    build_sub_button = '//*[@id="main"]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[4]/div/div/a'
    driver.implicitly_wait(5)
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
    date_of_order = "Tuesday, March 28, 2023"

    # Define date picker xpath and click on it
    pickup_date_button = f'//button[@data-day="{date_of_order}"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.CSS_SELECTOR, '.datepicker-activate').click()

    # Define specific date xpath and click on it
    pickup_time = "12:00 PM"
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, f'//button[@aria-label="{date_of_order}"]').click()


    # Select time
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((BY.ID, "input_pickupTime93"))
    )
    dropdown.click()

    options = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((BY.CSS_SELECTOR, "#input_pickupTime93 option"))
    )
    for option in options:
        if pickup_time in option.text:
            option.click()
            break

    time.sleep(1000)

    driver.quit()


if __name__ == '__main__':
    order_sub()