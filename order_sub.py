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
    # click on the text box and type in the location

    location_selection_textbox_path = '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input'
    address = 'St. John\'s Town Center'  # This is the address of the store we want to go to
    driver.find_element(BY.XPATH, location_selection_textbox_path).send_keys(address)
    #
    driver.find_element(BY.XPATH, location_selection_textbox_path).send_keys(u'\ue007')  # Press enter

    location_address = f'//button[@aria-label="Choose {address} as your store"]'

    correct_store_choose_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((BY.XPATH, location_address))
    )
    correct_store_choose_option.click()

    # driver.find_element(BY.XPATH, "//button[@aria-label=\"Choose St. John's Town Center as your store\"]").click()

    """Choosing store location
    
    This code above is needed because we initially block our location services.
    The input for choosing the location pops up automatically, so we click on the text box, enter an address, and press enter.
    The store elements are easy to locate because each has their own unique labels (eg. "Choose St. John's Town Center as your store").
    So, we use the address variable to find the correct store, wait for it to load, and then click on it. This exits the address prompt.
    
    """

    # Start ordering sub

    # Press build your own sub button on specific sub (which I've yet to configure to be customizable)
    build_sub_button = '//*[@id="main"]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[4]/div/div/a'
    driver.implicitly_wait(10)
    driver.find_element(BY.XPATH, build_sub_button).click()

    # Press customize sub button
    driver.implicitly_wait(5)
    customize_sub_button = '//*[@id="product-details-form-add-to-order"]/div[2]/div[2]/div/a/span'
    driver.find_element(BY.XPATH, customize_sub_button).click()

    # Press add to cart button
    driver.implicitly_wait(5)
    add_to_cart_button = '//*[@id="body-wrapper"]/div/div[2]/div/div/div[2]/button'
    driver.find_element(BY.XPATH, add_to_cart_button).click()

    # Instead of going through several more buttons, I go to this link below, which puts me in the checkout page without any more clicks
    driver.get('https://www.publix.com/shop-online/in-store-pickup/checkout')

    # A prompt pops up asking to confirm my location (always) and I click on the button to confirm it
    driver.implicitly_wait(5)
    confirm_store_location_button = '//*[@id="body-wrapper"]/div/div[2]/div/div[3]/div/div/button[2]'
    driver.find_element(BY.XPATH, confirm_store_location_button).click()

    # Click the checkout button
    driver.implicitly_wait(5)
    checkout_button = '//*[@id="two-column-container"]/div[2]/div/div/div[1]/div[2]/button'
    driver.find_element(BY.XPATH, checkout_button).click()

    # This is the form for entering the customer's information
    # I will have a class later that will input custom information for each customer

    # First name
    first_name_input = '//*[@name="FirstName"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, first_name_input).send_keys('John')

    # Last name
    last_name_input = '//*[@name="LastName"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, last_name_input).send_keys('Doe')

    # Phone number
    phone_number_input = '//*[@name="ContactPhone"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, phone_number_input).send_keys('904-555-5555')

    # Email
    email_input = '//*[@name="Email"]'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, email_input).send_keys('john.doe@gmail.com')

    # Click the next button, unlocking the next form below with the date and time pickers
    next_button = '//*[@id="content_22"]/form/div[3]/button'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, next_button).click()


    # Open up the date picker (calendar-style)
    driver.implicitly_wait(5)
    driver.find_element(BY.CSS_SELECTOR, '.datepicker-activate').click()
    time.sleep(2)  # This time sleep is neccessary. When the date picker is opened, the page rapidly scrolls to the bottom, and the wrong date is picked.

    # The date is easy to enter, as it is a calendar-style picker and each date has a unique label which we can use to find it
    # Pick a date
    date_of_order = "Wednesday, March 29, 2023"
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, f'//button[@aria-label="{date_of_order}"]').click()


    # Select time dropdown
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((BY.ID, "input_pickupTime93"))
    )
    dropdown.click()

    # The time is also easy to enter, as it is a dropdown-style picker and each time has a unique value which we can use to find it
    pickup_time = "2023-03-29T09:45:00"
    driver.find_element(BY.XPATH, f'//option[@value="{pickup_time}"]').click()

    # Click the next button, unlocking the next form below with the payment information
    next_button = '//*[@id="content_26"]/form/div[3]/div/button'
    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, next_button).click()

    # This is the payment information section, where instead of credit card info, I choose "pay in store"
    driver.find_element(BY.XPATH, '//*[@id="content_30"]/form/div[2]/div/div[1]/div[1]').click()

    # Later, here will be the click for the final submit button, which will put the order to the chosen deli officially

    # Quit the driver
    driver.quit()


if __name__ == '__main__':
    order_sub()