import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.selenium_app.helpers import webdriver_location_input

from backend.resources import create_webdriver
import helpers

def order_sub(self):
    driver = create_webdriver()

    # These are two different identifications for the browser to think it's a different browser
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


    try:
        accept_button = driver.find_element(By.XPATH,
                                            '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]')
        wait = WebDriverWait(driver, 10)
        if wait.until(EC.element_to_be_clickable((By.XPATH,
                                                  '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]'))):
            accept_button.click()
    except:
        pass

    print('made it past the except button')
    # Location chooser
    # click on the text box and type in the location

    location = "St. John\'s Town Center"
    webdriver_location_input(driver, location)
    # driver.find_element(BY.XPATH, "//button[@aria-label=\"Choose St. John's Town Center as your store\"]").click()

    # Click on the correct sub
    time.sleep(6)
    sandwich = self.requested_sub.strip()
    sandwich_xpath = f'//*[contains(text(),"{sandwich}")]'
    driver.find_element(By.XPATH, sandwich_xpath).click()

    # Start ordering sub
    time.sleep(1000)
    # Press build your own sub button on specific sub (which I've yet to configure to be customizable)
    build_sub_button = '//*[@id="main"]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[4]/div/div/a'
    driver.implicitly_wait(10)
    driver.find_element(By.XPATH, build_sub_button).click()

    # Press customize sub button
    driver.implicitly_wait(5)
    customize_sub_button = '//*[@id="product-details-form-add-to-order"]/div[2]/div[2]/div/a/span'
    driver.find_element(By.XPATH, customize_sub_button).click()

    # Press add to cart button
    driver.implicitly_wait(5)
    add_to_cart_button = '//*[@id="body-wrapper"]/div/div[2]/div/div/div[2]/button'
    driver.find_element(By.XPATH, add_to_cart_button).click()

    # Instead of going through several more buttons, I go to this link below, which puts me in the checkout page without any more clicks
    driver.get('https://www.publix.com/shop-online/in-store-pickup/checkout')

    # A prompt pops up asking to confirm my location (always) and I click on the button to confirm it
    driver.implicitly_wait(5)
    confirm_store_location_button = '//*[@id="body-wrapper"]/div/div[2]/div/div[3]/div/div/button[2]'
    driver.find_element(By.XPATH, confirm_store_location_button).click()

    # Click the checkout button
    driver.implicitly_wait(5)
    checkout_button = '//*[@id="two-column-container"]/div[2]/div/div/div[1]/div[2]/button'
    driver.find_element(By.XPATH, checkout_button).click()

    # This is the form for entering the customer's information
    # I will have a class later that will input custom information for each customer

    # First name
    first_name_input = '//*[@name="FirstName"]'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, first_name_input).send_keys('John')

    # Last name
    last_name_input = '//*[@name="LastName"]'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, last_name_input).send_keys('Doe')

    # Phone number
    phone_number_input = '//*[@name="ContactPhone"]'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, phone_number_input).send_keys('904-555-5555')

    # Email
    email_input = '//*[@name="Email"]'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, email_input).send_keys('john.doe@gmail.com')

    # Click the next button, unlocking the next form below with the date and time pickers
    next_button = '//*[@id="content_22"]/form/div[3]/button'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, next_button).click()


    # Open up the date picker (calendar-style)
    driver.implicitly_wait(5)
    driver.find_element(By.CSS_SELECTOR, '.datepicker-activate').click()
    time.sleep(2)  # This time sleep is neccessary. When the date picker is opened, the page rapidly scrolls to the bottom, and the wrong date is picked.

    # The date is easy to enter, as it is a calendar-style picker and each date has a unique label which we can use to find it
    # Pick a date
    date_of_order = "Wednesday, March 29, 2023"
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, f'//button[@aria-label="{date_of_order}"]').click()


    # Select time dropdown
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "input_pickupTime93"))
    )
    dropdown.click()

    # The time is also easy to enter, as it is a dropdown-style picker and each time has a unique value which we can use to find it
    pickup_time = "2023-03-29T09:45:00"
    driver.find_element(By.XPATH, f'//option[@value="{pickup_time}"]').click()

    # Click the next button, unlocking the next form below with the payment information
    next_button = '//*[@id="content_26"]/form/div[3]/div/button'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, next_button).click()

    # This is the payment information section, where instead of credit card info, I choose "pay in store"
    driver.find_element(By.XPATH, '//*[@id="content_30"]/form/div[2]/div/div[1]/div[1]').click()

    # Later, here will be the click for the final submit button, which will put the order to the chosen deli officially

    # Quit the driver
    driver.quit()


if __name__ == '__main__':
    order_sub()