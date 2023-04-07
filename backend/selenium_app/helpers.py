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


def generate_user_info():
    """Generate random user info

    This function will generate random user info for each customer.
    The pickup order requires a first name, last name, phone number, and email,
    yet none of this is used to update or inform the customer of their order, besides
    their name which is printed on the receipt that's stapled to the bag.

    So, I've chosen to randomly generate some funny names and emails so the user
    doesn't have to put any of their own information in. This is also a good way to
    test the app with different names and emails to make sure it's working properly.

    """

    prefix_options = ['Sir', 'Sir ', 'Grand Duke', 'Madam', 'Baron', 'Duchess', 'Count', 'Duke', 'Lord', 'Lady',
                      'Prince', 'Princess', 'King', 'Queen', '', '', '', '', '', '', '', '', '', '']

    suffix_options = ['McGee', 'Yeo', 'Von Humperdink', 'Von Schnitzel', 'The Magnificent', 'The Great', 'The Terrible',
                      'The Unstoppable', 'The Indomitable', 'The Invincible', '', '', '', '', '', '', '', '', '', '',
                      '']

    first_name_options = ['Wilfred', 'Skipps', 'Rigby', 'Vlad', 'Derwin', 'Yertle', 'Balthazar', 'Bartholomew', 'Looie',
                          'Zooie', 'Finnegan', 'Gulliver', 'Horatio', 'Isadora', 'Jasper', 'Lysander', 'Jo-Jo', 'Mack',
                          'Morris', 'Sneelock', 'Rolf', 'Zinn-a-zu', 'Harry', 'Herbie', 'Hawtch', 'Nutch',
                          'Sneedle', 'Umbus', 'Wump', 'Nook', 'Poozer', 'Luke', 'Foona', 'Norval', 'Doubt-trout']

    last_name_options = ['McBean', 'Vlad-i-Koff', 'Katz', 'Muffinpuff', 'Katzen-bein', 'Cubbins', 'o’Donald o’Dell',
                         'McSnazzy', 'Flapdoodle', 'Flibbertigibbet', 'McGrew', 'Who', 'Bar-ba-loots',
                         'McFuzz', 'Mulvaney', 'McCave', 'Wickersham', 'McGurk', 'Joat', 'De Breeze', 'Yookero',
                         'Sard', 'Potter', 'Haddow', 'Hart', 'Hawtch-Hawtcher','Gump', 'Fish', 'Lagoona']

    email_ending_options = ['@aol.com', '@yahoo.com', '@hotmail.com', '@yandex.com', '@bungus.com', '@saxophone.com']

    random_prefix = random.choice(prefix_options)
    random_suffix = random.choice(suffix_options)
    random_first_name = random.choice(first_name_options)
    random_last_name = random.choice(last_name_options)

    first_name = f"{random_prefix} {random_first_name}"
    last_name = f"{random_last_name} {random_suffix}"

    email = f"{random_first_name.lower()}.{random_last_name.lower()}{random.choice(email_ending_options)}"

    # This is an unused, but valid phone number
    phone_number = '321-556-0291'

    return first_name, last_name, email, phone_number
