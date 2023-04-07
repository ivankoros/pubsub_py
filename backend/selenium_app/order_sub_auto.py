import random
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from backend.selenium_app.helpers import webdriver_location_input, generate_user_info
from backend.twilio_app.helpers import SubOrder
from datetime import datetime

from backend.resources import create_webdriver


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
    time.sleep(
        random.randint(2, 3))  # Sleep for a couple of seconds before doing anything, important to not get blocked

    try:
        accept_button = driver.find_element(By.XPATH,
                                            '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]')
        wait = WebDriverWait(driver, 10)
        if wait.until(EC.element_to_be_clickable((By.XPATH,
                                                  '//button[contains(@class,"button--primary") and contains(@class,"button--lg") and contains(text(),"Accept and continue")]'))):
            accept_button.click()
    except NoSuchElementException:
        pass

    # Store location input
    location = self.store_name.strip()
    official_location_name = webdriver_location_input(driver, location)
    print(f"location name: {official_location_name}")
    # driver.find_element(BY.XPATH, "//button[@aria-label=\"Choose St. John's Town Center as your store\"]").click()

    # Click on the correct sub
    pick_sandwich = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[contains(text(),"{self.requested_sub.strip()}")]'))
    )
    sandwich_name = pick_sandwich.text
    pick_sandwich.click()
    print(f"Selected sandwich: {sandwich_name}")

    # Press customize sub button
    driver.implicitly_wait(5)
    customize_sub_button = '//*[@id="product-details-form-add-to-order"]/div[2]/div[2]/div/a/span'
    driver.find_element(By.XPATH, customize_sub_button).click()

    # Press add to cart button
    driver.implicitly_wait(5)
    add_to_cart_button = '//*[@id="body-wrapper"]/div/div[2]/div/div/div[2]/button'
    driver.find_element(By.XPATH, add_to_cart_button).click()
    time.sleep(2)

    # Instead of going through several more buttons, I go to this link below, which puts me in the checkout page without any more clicks
    driver.get('https://www.publix.com/shop-online/in-store-pickup/checkout')

    # A prompt pops up asking to confirm my location (sometimes) and I click on the button to confirm it
    driver.implicitly_wait(3)
    confirm_store_location_button = '//*[@id="body-wrapper"]/div/div[2]/div/div[3]/div/div/button[2]'

    try:
        confirm_location_element = driver.find_element(By.XPATH, confirm_store_location_button)
        if confirm_location_element.is_displayed():
            confirm_location_element.click()
    except NoSuchElementException:
        print("Confirm location element not found, continuing...")

    # Input info for pickup

    first_name, last_name, email, phone_number = generate_user_info()
    print(first_name, last_name, email, phone_number)

    driver.find_element(By.XPATH, '//*[@name="FirstName"]').send_keys(first_name)

    driver.find_element(By.XPATH, '//*[@name="LastName"]').send_keys(last_name)

    driver.find_element(By.XPATH, '//*[@name="ContactPhone"]').send_keys(phone_number)

    driver.find_element(By.XPATH, '//*[@name="Email"]').send_keys(email)

    # Click the next button, unlocking the next form below with the date and time pickers
    next_button = '//*[@id="content_22"]/form/div[3]/button'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, next_button).click()

    # Open up the date picker (calendar-style)
    driver.implicitly_wait(5)
    driver.find_element(By.CSS_SELECTOR, '.datepicker-activate').click()
    time.sleep(2)  # This time sleep is necessary. When the date picker is opened, the page rapidly scrolls to the bottom, and the wrong date is picked.

    # The date is easy to enter, as it is a calendar-style picker and each date has a unique label which we can use to find it
    date_of_order = self.date_of_order
    """
    This date is currently not being used, it's just selecting the first date in the calendar, which is today.
    I will add functionality to select a date in the future, but for now, it's just today.
    
    """
    driver.implicitly_wait(5)

    driver.find_element(By.XPATH, value='//*[contains(@aria-label, "Today")]').click()

    # Select the pickup time
    time_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//select[@name="pickupTime"] '))
    )
    time_dropdown.click()

    select = Select(time_dropdown)

    all_times = driver.find_elements(By.XPATH, '//span[@class="time-item"]')
    pickup_time = all_times[1].text
    print(pickup_time)

    select.select_by_index(1)  # Soonest pickup time (in around 30 minutes)

    # Click the next button, unlocking the next form below with the payment information
    next_button = '//*[@id="content_26"]/form/div[3]/div/button'
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH, next_button).click()

    # This is the payment information section, where instead of credit card info, I choose "pay in store"

    driver.find_element(By.XPATH, '//*[@id="content_30"]/form/div[2]/div/div[1]/div[1]').click()
    print("Payment info entered successfully")

    # Later, here will be the click for the final submit button, which will put the order to the chosen deli officially

    driver.quit()
    print("Driver quit and order submitted successfully")

    # Update the SubOrder object with the order feedback

    self.first_name = first_name
    self.last_name = last_name
    self.store_name = official_location_name
    self.ordered_sandwich_name = sandwich_name
    self.time_of_order = pickup_time

    feedback = SubOrder.order_feedback(self)
    print(feedback)

    return self


if __name__ == '__main__':
    order = SubOrder(requested_sub='Publix Italian',
                     store_name='St. John\'s Town Center',
                     date_of_order=datetime.today().date().strftime("%A, %B %d, %Y"))
    order_sub(order)
