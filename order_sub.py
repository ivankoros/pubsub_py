from main import initialize_database
from main import create_webdriver
from main import click_random_deal
from main import scroll_down
import random
import time
from selenium.webdriver.common.by import By as BY

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
        driver.get("https://www.publix.com/search?searchTerm=sub&srt=products")

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    time.sleep(random.randint(2, 3))

    scroll_down(driver)

    build_sub_button = '//*[@id="main"]/div[2]/div/div[2]/div[1]/div[2]/div[2]/div/div/div[5]/div/div[2]/div[4]/div/div/a/span'

    driver.implicitly_wait(5)
    driver.find_element(BY.XPATH, build_sub_button).click()
    time.sleep(5)

    driver.implicitly_wait(5)
    customize_sub_button = '//*[@id="product-details-form-add-to-order"]/div[2]/div[2]/div/a/span'
    driver.find_element(BY.XPATH, customize_sub_button).click()
    time.sleep(5)

    driver.quit()

if __name__ == '__main__':
    order_sub()