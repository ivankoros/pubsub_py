import logging
from time import sleep
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.twilio_app.helpers import fuzzy_string_match


def webdriver_location_input(driver, store_name, store_address):
    """Choosing store location

    This code above is needed because we initially block our location services.
    The input for choosing the location pops up automatically, so we click on the text box, enter an address, and press enter.
    The store elements are easy to locate because each has their own unique labels (e.g. "Choose St. John's Town Center as your store").
    So, we use the address variable to find the correct store, wait for it to load, and then click on it. This exits the address prompt.

    """
    # choose_location_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, '//button[@id="choose-store-btn"]')))

    choose_location_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,
                                        '/html/body/div/div/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div/div/div/button'))
    )

    #driver.execute_script("arguments[0].click();", choose_location_button)
    choose_location_button.click()

    location_selection_textbox_path = '//input[@aria-label="Search locations"]'

    textbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, location_selection_textbox_path)))

    textbox.send_keys(store_address)

    driver.find_element(By.XPATH, location_selection_textbox_path).send_keys(u'\ue007')  # Press enter
    logging.info('Pressed enter')
    location_address = f'//button[@aria-label="Choose {store_name} as your store"]'
    logging.info(f'Looking for store: {store_name}')
    correct_store_choose_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, location_address))
    )

    store_element = correct_store_choose_option.find_element(By.XPATH, './ancestor::li')

    # Find the header element within the store element using XPath
    header_element = store_element.find_element(By.CSS_SELECTOR, '.store-info .title-wrapper h3')

    correct_store_choose_option.click()
    logging.info(f'Clicked on store: {store_name}')
    official_location_name = header_element.text

    return official_location_name


def build_sub_link(self, customization_dictionary: dict = None):

    sub_no_apostrophe = re.sub("'", "", self.sub_name.lower())
    sub_hyphen_split = re.sub(" ", "-", sub_no_apostrophe)

    sub_link = f"https://www.publix.com/pd/{sub_hyphen_split}/{self.sub_id}"

    # Map the customizations to the correct elements
    customizations_map = {
        # Size
        "Half": "9-24",
        "Whole": "9-25",

        # Bread
        "Italian 5 Grain": "5-29",
        "White": "5-27",
        "Whole Wheat": "5-28",
        "Flatbread": "5-1062",
        "No Bread (Make it a Salad) - Lettuce Base": "5-1518",
        "No Bread (Make it a Salad) - Spinach Base": "5-1519",

        # Cheese
        "Pepper Jack": "6-1925",
        "Cheddar": "6-38",
        "Muenster": "6-39",
        "Provolone": "6-35",
        "Swiss": "6-34",
        "White American": "6-37",
        "Yellow American": "6-36",
        "No Cheese": "6-40",

        # Extras
        "Double Meat": "185-1",
        "Double Cheese": "185-2",
        "Bacon": "185-3",
        "Guacamole": "185-723",
        "Hummus": "185-970",

        # Toppings
        "Banana Peppers": "10-15",
        "Black Olives": "10-19",
        "Boar's Head® Garlic Pickles": "10-18",
        "Cucumbers": "10-120",
        "Dill Pickles": "10-17",
        "Green Peppers": "10-12",
        "Jalapeno Peppers": "10-16",
        "Lettuce": "10-8",
        "Onions": "10-10",
        "Spinach": "10-141",
        "Tomato": "10-9",
        "Salt": "10-20",
        "Pepper": "10-21",
        "Oregano": "10-23",
        "Oil & Vinegar Packets": "10-22",

        # Condiments
        "Boar's Head Honey Mustard": "186-7",
        "Boar's Head Spicy Mustard": "186-6",
        "Mayonnaise": "186-4",
        "Yellow Mustard": "186-5",
        "Vegan Ranch Dressing": "186-911",
        "Buttermilk Ranch": "186-2377",
        "Boar's Head Pepperhouse Gourmaise": "186-145",
        "Boar's Head Chipotle Gourmaise": "186-1522",
        "Boar's Head Sub Dressing": "186-1521",
        "Deli Sub Sauce": "186-1523",

        # Heating Options
        "Pressed": "8-41",
        "Toasted": "8-42",
        "No Thanks": "8-43",

        # TODO fix this Make it a Combo
        # "Yes": "183-775",
        # "No Thanks": "183-775",
    }

    if customization_dictionary:
        selected_ids = []

        for category, options in customization_dictionary.items():

            if options == "None" or not options:
                continue
            elif isinstance(options, str):
                options = [choice for choice in options.split(", ")]

                for topping in options:
                    if fuzzy_string_match(topping, customizations_map.keys()):
                        topping_found = fuzzy_string_match(topping, customizations_map.keys())
                        selected_ids.append(customizations_map[topping_found])

                        print(f"SUCCESS: Found {topping} as {topping_found} in customizations_map")
                    else:
                        print(f"FAILURE: Could not find {topping} in customizations_map")

        # Add heating option and size if not specified
        if not re.match(r"8-\d+", selected_ids[0]):
            selected_ids.insert(0, "8-43")
        if not re.match(r"9-\d+", selected_ids[0]):
            selected_ids.insert(0, "9-25")

        link_list = ",".join(indv_id for indv_id in selected_ids)
        sub_link += f"/builder/?modifiers={link_list}&quantity=1"

    print(f"\nSub link: {sub_link} \n")
    return sub_link
