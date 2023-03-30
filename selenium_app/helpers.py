from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def webdriver_location_input(driver, location):
    location_selection_textbox_path = '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input'
    address = location  # This is the address of the store we want to go to
    driver.find_element(By.XPATH, location_selection_textbox_path).send_keys(address)
    #
    driver.find_element(By.XPATH, location_selection_textbox_path).send_keys(u'\ue007')  # Press enter

    location_address = f'//button[@aria-label="Choose {address} as your store"]'

    correct_store_choose_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, location_address))
    )
    correct_store_choose_option.click()
