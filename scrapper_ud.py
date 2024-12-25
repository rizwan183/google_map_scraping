import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import json


class WebScraper:
    def __init__(self):
        self.driver = None
        self.find_by={
            "id":By.ID,
            'class_name':By.CLASS_NAME,
            'css_selector':By.CSS_SELECTOR,
            "x_path":By.XPATH,
            "name":By.NAME,
            "link_text":By.LINK_TEXT,
            "partial_link":By.PARTIAL_LINK_TEXT,
            "tag":By.TAG_NAME
        }

    def setup_driver(self):
        # Initialize UserAgent object to generate random user agent strings
        user_agent = UserAgent()

        # Get a random user agent string to spoof the browser's identity
        fake_user_agent = user_agent.random

        # Configure Chrome options
        chrome_options = Options()

        # Add the random user agent string to Chrome options
        chrome_options.add_argument(f'user-agent={fake_user_agent}')

        # Disable GPU hardware acceleration to improve stability and performance
        chrome_options.add_argument("--disable-gpu")

        # Disable Chrome extensions to reduce resource usage and potential interference
        chrome_options.add_argument("--disable-extensions")

        # Set the initial window size of the browser
        chrome_options.add_argument("--window-size=1440x900")

        # Exclude certain automation-related switches to make the browser less detectable as a bot
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        # Disable Blink features that are controlled by automation to reduce detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # Ensure the browser starts in a maximized window for a consistent view
        chrome_options.add_argument("--start-maximized")

        # Reduce RAM usage to prevent issues in environments with limited memory
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Disable the sandbox security feature, which can help prevent issues in certain environments
        # Note: This should be used with caution as it reduces security
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-popup-blocking")
        # chrome_options.add_argument("--headless=new")

        # Initialize the Chrome WebDriver with the specified options
        self.driver = uc.Chrome(use_subprocess=False,options=chrome_options)


    def open_url(self, url: str) -> None:
        """
        open url in chrome driver
        :param url:
        :return:
        """
        if not self.driver:
            """
            if driver is none create driver
            """
            self.setup_driver()

        # Open a website
        self.driver.get(url)

        time.sleep(1)

    def click_by_id(self, element_id: str) -> None:
        """
        click an element by element_id
        :param element_id:
        :return:
        """
        if not self.driver:
            self.setup_driver()
        self.driver.find_element(By.ID, element_id).click()


    def find_element_by(self,find_by:str,what_to_find:str,multi:bool=False):
        if multi:
            return self.driver.find_elements(self.find_by[find_by],what_to_find)
        else:
            try:
                return self.driver.find_element(self.find_by[find_by],what_to_find)
            except Exception as error:

                return None



    def scroll_by_height(self, element) -> any:
        self.driver.execute_script("arguments[0].scrollTop=arguments[0].scrollHeight", element)



    def refresh_page(self) -> None:
        """
        refresh current page
        :return:
        """
        if not self.driver:
            self.setup_driver()
        # Refresh the page
        self.driver.refresh()
        time.sleep(5)

    def get_cookies(self) -> str:
        """
        get cookies of current site
        :return: current site cookies
        """
        if not self.driver:
            self.setup_driver()

        # Get cookies
        cookies = self.driver.get_cookies()

        # Convert cookies to JSON format
        cookies_json = json.dumps(cookies, indent=4)
        return cookies_json

    def load_cookies(self, cookies: str) -> None:
        """
        insert cookies in web site
        :param cookies:
        :return:
        """

        if not self.driver:
            self.setup_driver()

        # Add each cookie to the Selenium session
        for cookie in json.loads(cookies):
            self.driver.add_cookie(cookie)

    def close_driver(self) -> None:
        """
        close driver
        :return:
        """
        if self.driver:
            self.driver.quit()

    def close_tab(self) -> None:
        """
        close tab and switch in main tab
        :return:
        """
        if self.driver:
            self.driver.close()
            # Switch back to the original tab
            self.driver.switch_to.window(self.driver.window_handles[0])
    def page_source(self):
        return self.driver.page_source

    def open_new_tab(self) -> None:
        """
        open new tab
        :return:
        """
        print("Before opening new tab:", self.driver.window_handles)
        self.driver.execute_script("window.open('');")
        time.sleep(.33)
        # Access the new tab
        self.driver.switch_to.window(self.driver.window_handles[1])
        # self.driver.switch_to.window(self.driver.window_handles[1])


# Example usage:
if __name__ == "__main__":
    # Create an instance of the WebScraper class
    scraper = WebScraper()
    # Close the WebDriver
    scraper.close_driver()
