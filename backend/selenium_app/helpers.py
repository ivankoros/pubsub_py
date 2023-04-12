import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def webdriver_location_input(driver, store_name, store_address):
    """Choosing store location

    This code above is needed because we initially block our location services.
    The input for choosing the location pops up automatically, so we click on the text box, enter an address, and press enter.
    The store elements are easy to locate because each has their own unique labels (e.g. "Choose St. John's Town Center as your store").
    So, we use the address variable to find the correct store, wait for it to load, and then click on it. This exits the address prompt.

    """
    # choose_location_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, '//button[@id="choose-store-btn"]')))

    choose_location_button = driver.find_element(By.XPATH, '/html/body/div/div/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div/div/div/button')
    # /html/body/div/div/section/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div/div/div/button
    driver.execute_script("arguments[0].click();", choose_location_button)
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


def input_customizations(driver):
    custom_dict = {'Bread': 'Whole Wheat',
                   'Cheese': 'Swiss',
                   'Condiments': "Boar's Head Honey Mustard",
                   'Extras': 'Hummus',
                   'Heating Options': 'Toasted',
                   'Make it a Combo': 'None',
                   'Size': 'Half',
                   'Toppings': 'Banana Peppers, Dill Pickles, Lettuce, Oil & Vinegar Packets'}

    for key, value in custom_dict.items():
        # Find the label element for the customization
        #label_element_xpath = f"//label[contains(text(), '{key}')]"
        #label_element = driver.find_element(By.XPATH, label_element_xpath)

        print(f"Label element: {key}")
        from time import sleep

        # Find the customization element within the label element
        customization_element = label_element.find_element(By.XPATH, './following-sibling::div')

        # Find the customization option element within the customization element
        customization_option_element_xpath = f"//label[contains(text(), '{value}')]"
        customization_option_element = customization_element.find_element(By.XPATH, customization_option_element_xpath)

        # Click on the customization option element
        customization_option_element.click()

    whole_element_xpath = "//p[contains(text(), 'Whole')]/ancestor::label"
    driver.find_element(By.XPATH, whole_element_xpath).click()

    pass
