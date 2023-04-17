import datetime
import random
import time
import re

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from backend.twilio_app.helpers import SubOrder
from datetime import datetime

from backend.resources import create_webdriver

"""
Consider creating a separate function to handle setting up the driver, such as initialize_driver(), which will create the webdriver and set the user agent.

Create a function to handle finding and clicking elements, like click_element(driver, xpath, wait_time) to reduce the repetitive code.

Create a function to input user information like input_user_info(driver, first_name, last_name, email, phone_number) to make the main function shorter and more readable.

Consider creating a function to handle the date and time selection, like select_pickup_date_and_time(driver).
"""


class OrderSubFunctionDiagnostic():
    def __init__(self):
        self.selected_store_location = None
        self.selected_sandwich = None
        self.run_speed = None
        self.user_agent = None
        self.official_location_name = None
        self.sandwich_name = None
        self.pickup_time = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.phone_number = None

    def __repr__(self):
        output = f"OrderSubFunctionDiagnostic:\n" \
                 f"Selected store location: {self.selected_store_location}\n" \
                 f"Selected sandwich: {self.selected_sandwich}\n" \
                 f"User agent: {self.user_agent}\n" \
                 f"Official location name: {self.official_location_name}\n" \
                 f"Selected sandwich: {self.sandwich_name}\n" \
                 f"First pickup time: {self.pickup_time}\n" \
                 f"First name: {self.first_name}\n" \
                 f"Last name: {self.last_name}\n" \
                 f"Email: {self.email}\n" \
                 f"Phone number: {self.phone_number}\n" \
                 f"Run speed: {self.run_speed}"
        return output


def order_sub(self: SubOrder, diagnostic: OrderSubFunctionDiagnostic, use_user_agent: bool = False,
              actually_submit: bool = False):
    from backend.selenium_app.helpers import webdriver_location_input, build_sub_link
    start = time.perf_counter()

    driver = create_webdriver()

    # These are two different identifications for the browser to think it's a different browser
    user_agent_array = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]

    # This is extremely important, many times, the first or even second user agent will be blocked (randomly),
    # so they're needed to change the identity of the browser to successfully load in the page (the hardest part)

    sub_link = build_sub_link(self=self)

    if use_user_agent:
        for i in range(len(user_agent_array)):
            # Setting user agent iteratively as Chrome 108 and 107
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent_array[i]})
            diagnostic.user_agent = driver.execute_script("return navigator.userAgent;")
    else:
        driver.get(sub_link)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    time.sleep(random.randint(2, 5))

    try_count = 0
    while try_count < 3:
        try:
            driver.get(sub_link)
            webdriver_location_input(driver=driver,
                                     store_name=self.store_name,
                                     store_address=self.store_address)

            print(f"Successfully loaded in the page in {time.perf_counter() - start} seconds")
            break
        except TimeoutException:
            driver.get(sub_link)
            time.sleep(5)
            print(f"Page didn't load in time, trying again... ({try_count + 1}/3)")
            try_count += 1

    # Click on the sub link
    customized_sub_link = build_sub_link(self=self,
                                         customization_dictionary=self.customization_dictionary)

    driver.get(customized_sub_link)

    # Press add to cart button
    add_to_cart_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#builder-add-to-order-btn")))
    add_to_cart_button.click()

    print("This is a forced sleep to show the ingredients have been chosen: resuming in...")
    for x in range(20, 0, -1):
        time.sleep(1)
        print(f"{x}")
    print("Resuming...")

    """ Go directly to check out by going to this link
    Instead of clicking review order, confirming store, and then clicking the checkout button,
    after pressing "add to cart" you can go directly to the checkout page by going to this link
    
    However, because this usually needs to load, I need a dedicated time.sleep to wait for the 
    sub to be added to the cart which we're going to. Otherwise, the sub won't be in the cart when
    we go to the checkout page.
    """

    driver.get('https://www.publix.com/shop-online/in-store-pickup/checkout')

    # A prompt pops up asking to confirm my location (sometimes) and I click on the button to confirm it
    try:
        confirm_location_element = driver.find_element(By.XPATH,
                                                       '//*[@id="body-wrapper"]/div/div[2]/div/div[3]/div/div/button[2]')
        if confirm_location_element.is_displayed():
            confirm_location_element.click()
    except NoSuchElementException:
        pass

    # Input info for pickup
    driver.find_element(By.XPATH, '//*[@name="FirstName"]').send_keys(self.first_name)

    driver.find_element(By.XPATH, '//*[@name="LastName"]').send_keys(self.last_name)

    driver.find_element(By.XPATH, '//*[@name="ContactPhone"]').send_keys(self.phone_number)

    driver.find_element(By.XPATH, '//*[@name="Email"]').send_keys(self.email)

    # Click the next button, unlocking the next form below with the date and time pickers
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content_22"]/form/div[3]/button'))
    )
    next_button.click()

    # Open up the date picker (calendar-style)
    datepicker = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.datepicker-activate'))
    )
    # This time sleep is necessary. When the date picker is opened, the page rapidly scrolls to the bottom, and the wrong date is picked.
    datepicker.click()
    time.sleep(2)

    # The date is easy to enter, as it is a calendar-style picker and each date has a unique label which we can use to find it
    """
    This date is currently not being used, it's just selecting the first date in the calendar, which is today.
    I will add functionality to select a date in the future, but for now, it's just today.
    
    """
    driver.implicitly_wait(5)

    date_dropdown = driver.find_element(By.XPATH, value='//*[contains(@aria-label, "Today")]')
    date_dropdown.click()

    # Select the pickup time
    time_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//select[@name="pickupTime"] '))
    )
    # time_dropdown.click()

    select = Select(time_dropdown)
    select.select_by_index(1)

    pickup_time_html = select.options[1].get_attribute('innerHTML')

    extracted_time = re.search(r'<span class="time-item">(.+)</span>', pickup_time_html).group(1)

    # Click the next button, unlocking the next form below with the payment information
    final_next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "content")]/form/div[3]/div/button'
                                    )))

    final_next_button.click()

    # This is the payment information section, where instead of credit card info, I choose "pay in store"
    pay_in_store_button = driver.find_element(By.CSS_SELECTOR, 'input[type="radio"][value="Pay in-store"]')
    driver.execute_script("arguments[0].click();", pay_in_store_button)

    # Later, here will be the click for the final submit button, which will put the order to the chosen deli officially
    if actually_submit:
        submit_order_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Place")]/ancestor::button'))
        )
        submit_order_button.click()

    print("This is a forced sleep to show the confirmation page, closing in 10 seconds...")
    for x in range(10, 0, -1):
        time.sleep(1)
        print(f"{x}")
    print("Closing...")

    print("SUCCESS: Order placed!")
    driver.quit()

    # Stop the timer
    end = time.perf_counter()

    # Update the SubOrder object with accurate information
    self.time_of_order = extracted_time

    # Update the diagnostic object with accurate information
    diagnostic.pickup_time = extracted_time
    diagnostic.run_speed = round(end - start)

    return self, diagnostic


if __name__ == '__main__':
    order = SubOrder(sub_name="Publix Italian Sub",
                     sub_id='BMO-DSB-100013',
                     store_name="St. John's Town Center",
                     store_address='4413 Town Center Pkwy #100, Jacksonville',
                     date_of_order=datetime.today().date().strftime("%A, %B %d, %Y"),
                     time_of_order='12:00 PM',
                     first_name='John',
                     last_name='Doe',
                     phone_number='(555) 555-5555',
                     email='John.Doe@gmail.com',
                     customization_dictionary={'Bread': 'White',
                                               'Cheese': None,
                                               'Condiments': 'Mayonnaise',
                                               'Extras': None,
                                               'Heating Options': None,
                                               'Make it a Combo': None,
                                               'Size': 'Whole',
                                               'Toppings': ['Tomato', 'Lettuce']})

    order_feedback, diagnostic = order_sub(order, diagnostic=OrderSubFunctionDiagnostic(), use_user_agent=True)

    # print(diagnostic)
    # print(SubOrder.__str__(order_feedback))
    print("SUCCESS: Sub order placed successfully!")
