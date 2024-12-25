import time
from scrapper_ud import WebScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd


def gmap_scraper(target: str) -> None:
    """
    This function scrapes business information from Google Maps based on a search query.
    It uses Selenium for web scraping and BeautifulSoup for HTML parsing to extract business
    details like name, rating, reviews, address, website, phone number, and plus code.

    Args:
        target (str): The search query (e.g., "college near me") to search on Google Maps.

    Returns:
        None: The function saves the extracted data to a CSV file and does not return any value.
    """

    # Initialize the WebScraper object to control the web driver
    web_driver = WebScraper()
    web_driver.setup_driver()  # Setup web driver (e.g., ChromeDriver)

    # Open the Google Maps URL
    web_driver.open_url("https://www.google.com/maps")
    time.sleep(10)  # Wait for the page to load

    # Click on "Continue" button if it exists (handles potential popups)
    continue_btn = web_driver.find_element_by(find_by="css_selector",
                                              what_to_find='button[class="vrdm1c K2FXnd Oz0bd oNZ3af"]', multi=False)
    if continue_btn is None:
        continue_btn = web_driver.find_element_by(find_by="css_selector",
                                                  what_to_find='button[class="vfi8qf qgMOee"]',
                                                  multi=False)
    if continue_btn:
        continue_btn.click()
    time.sleep(20)  # Wait for 20 seconds after clicking continue

    # Find the search box and input the target query (business or location)
    search_box = web_driver.find_element_by(find_by="id", what_to_find="searchboxinput", multi=False)
    if search_box is None:
        # Try other methods to find the search box if the ID-based search fails
        search_box = web_driver.find_element_by(find_by="class_name", what_to_find="mqxVAc", multi=False)
        if search_box is None:
            search_box = web_driver.find_element_by(find_by="id", what_to_find="ml-searchboxinput", multi=False)
            if search_box is None:
                search_box = web_driver.find_element_by(find_by="x_path",
                                                        what_to_find="/html/body/div[2]/div[15]/div/div/div/div[2]/div[1]/form/div/div/input",
                                                        multi=False)
    # Enter the target search query into the search box
    search_box.send_keys(target)

    try:
        # Click the search button or press Enter if clicking fails
        web_driver.click_by_id('searchbox-searchbutton')
        time.sleep(10)  # Wait for the results to load
    except:
        search_box.send_keys(Keys.ENTER)

    # Locate the div element for the search results
    scroll = web_driver.find_element_by(find_by="css_selector", what_to_find="div[aria-label^='Results']")

    # Scroll through the results until the last element is found
    while True:
        web_driver.scroll_by_height(scroll)  # Scroll down
        time.sleep(2)  # Wait for the scroll to load new data
        last_element = web_driver.find_element_by(find_by="css_selector",
                                                  what_to_find='div.m6QErb.XiKgde.tLjsW.eKbjU div.PbZDve p.fontBodyMedium span.HlvSq')
        if last_element:
            break  # Break the loop if the last element is found

    # Extract the business elements from the page
    businesses = web_driver.find_element_by(find_by='css_selector', what_to_find='div.Nv2PK.THOPZb.CpccDe ', multi=True)
    if len(businesses) == 0:
        businesses = web_driver.find_element_by(find_by='css_selector', what_to_find='div.Nv2PK.Q2HXcd.THOPZb ',
                                                multi=True)

    all_businesses = []  # List to store the extracted business details

    # Loop through each business and extract relevant information
    for business in businesses:
        find_a = business.find_element(By.TAG_NAME, "a")
        url = find_a.get_attribute('href')  # Get the URL of the business page
        web_driver.open_new_tab()  # Open a new tab
        web_driver.open_url(url=url)  # Open the business URL in the new tab
        time.sleep(3)  # Wait for the page to load
        page_source = web_driver.page_source()  # Get the page source of the business page
        soup = BeautifulSoup(page_source, 'html.parser')  # Parse the HTML with BeautifulSoup

        # Extract business details
        info_section = soup.find('div', class_='m6QErb XiKgde')
        details = {}

        # Extract business name
        name_tag = soup.find('h1', class_='DUwDvf lfPIob')
        name = name_tag.text.strip() if name_tag else "Name not found"

        # Extract rating and reviews
        rating_section = soup.find('div', class_='fontBodyMedium dmRWX')
        if rating_section:
            rating_span = rating_section.find('span', {'aria-hidden': 'true'})
            rating = rating_span.text.strip() if rating_span else "Rating not found"
            reviews_span = rating_section.find('span', {'aria-label': lambda x: x and 'reviews' in x})
            reviews = reviews_span['aria-label'] if reviews_span else "Reviews not found"
        else:
            rating = 0
            reviews = 0

        details.update({"business_name": name, "rating": rating, "reviews": reviews})

        # Extract additional business information like address, website, and phone number
        if info_section:
            address_button = info_section.find('button', {'data-item-id': 'address'})
            if address_button:
                details['Address'] = address_button.find('div', class_='Io6YTe').text.strip()

            website_link = info_section.find('a', {'data-item-id': 'authority'})
            if website_link:
                details['Website'] = website_link.get('href')

            phone_button = info_section.find('button', {'data-item-id': lambda x: x and x.startswith('phone:')})
            if phone_button:
                details['Phone'] = phone_button.find('div', class_='Io6YTe').text.strip()

            plus_code_button = info_section.find('button', {'data-item-id': 'oloc'})
            if plus_code_button:
                details['Plus Code'] = plus_code_button.find('div', class_='Io6YTe').text.strip()

        # Append the details of the business to the list
        all_businesses.append(details)
        web_driver.close_tab()  # Close the tab after scraping

    # Convert the list of business details to a pandas DataFrame
    df = pd.DataFrame(all_businesses)

    # Sort the DataFrame by 'Rating' in descending order
    df_sorted = df.sort_values(by="Rating", ascending=False)

    # Save the sorted DataFrame to a CSV file
    csv_file = "map.csv"
    df_sorted.to_csv(csv_file, index=False)

    # Print the success message with the file path
    print(f"Data has been saved to {csv_file}")
    time.sleep(10)


# Entry point for the script
if __name__ == "__main__":
    search = "college near me"  # Example search query
    gmap_scraper(search)  # Call the scraper function
