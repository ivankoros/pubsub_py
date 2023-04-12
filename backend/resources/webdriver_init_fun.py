from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

def create_webdriver():
    """Create a selenium webdriver for the bot to use

    Returns:
        webdriver: The selenium webdriver
    """
    # Selenium runtime options
    options = uc.ChromeOptions()
    #options.add_argument("--incognito")
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #options.add_experimental_option("useAutomationExtension", False)
    options.set_capability("acceptInsecureCerts", True)
    options.set_capability("acceptSslCerts", True)
    options.set_capability("unhandledPromptBehavior", "accept")
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_argument("--deny-permission-prompts")
    options.add_experimental_option("prefs", prefs)
    # one of the accept terms paths: /html/body/div[1]/div/div/div[3]/div/div/button
    """ Add options to selenium runtime
        --headless: Run without opening a window
        --disable-blink-features=AutomationControlled: Disable the "Chrome is being controlled by automated test software" message
        --incognito: Run in incognito mode
        Exclude switches and useAutomationExtension both remove identifiers for selenium being used as an automated test, which chrome doesnt like

        The options are added to the webdriver.Chrome() function which is passed to the webdriver and executed

    """

    # Download the latest chromium webdriver to mimic Chrome browser
    driver = uc.Chrome(options=options)

    return driver
