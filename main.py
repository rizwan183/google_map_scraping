import time
from scrapper_ud import WebScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
def gmap_scraper(target: str) -> None:
    """
    gmap scraper
    :return:
    """
    web_driver = WebScraper()
    # setup web driver
    web_driver.setup_driver()

    # open gmap url
    web_driver.open_url("https://www.google.com/maps")
    time.sleep(10)

    continue_btn = web_driver.find_element_by(find_by="css_selector", what_to_find='button[class="vrdm1c K2FXnd Oz0bd oNZ3af"]',multi=False)
    if continue_btn is None:
        continue_btn = web_driver.find_element_by(find_by="css_selector",
                                                  what_to_find='button[class="vfi8qf qgMOee"]',
                                                  multi=False)
    if continue_btn:
        continue_btn.click()
    time.sleep(20)



    # find search box
    search_box = web_driver.find_element_by(find_by="id",what_to_find="searchboxinput",multi=False)
    if search_box is None:
        search_box = web_driver.find_element_by(find_by="class_name", what_to_find="mqxVAc", multi=False)
        if search_box is None:
            search_box = web_driver.find_element_by(find_by="id", what_to_find="ml-searchboxinput", multi=False)
            if search_box is None:
                search_box = web_driver.find_element_by(find_by="x_path", what_to_find="/html/body/div[2]/div[15]/div/div/div/div[2]/div[1]/form/div/div/input", multi=False)
    # fill search box with target value
    search_box.send_keys(target)
    try:
        # click on search button
        web_driver.click_by_id('searchbox-searchbutton')
        time.sleep(10)
    except:
        search_box.send_keys(Keys.ENTER)
    scroll = web_driver.find_element_by(find_by="css_selector",what_to_find="div[aria-label^='Results']")
    while True:
        web_driver.scroll_by_height(scroll)
        time.sleep(2)
        last_element = web_driver.find_element_by(find_by="css_selector",
            what_to_find='div.m6QErb.XiKgde.tLjsW.eKbjU div.PbZDve p.fontBodyMedium span.HlvSq')
        # print("last_element",last_element)
        if last_element:
            # print("break")
            break
    businesses = web_driver.find_element_by(find_by='css_selector',what_to_find='div.Nv2PK.THOPZb.CpccDe ',multi=True)
    # print("businesses",businesses)
    if len(businesses)==0:
        businesses = web_driver.find_element_by(find_by='css_selector', what_to_find='div.Nv2PK.Q2HXcd.THOPZb ',
                                                multi=True)
    # print("businesses", businesses)
    all_businesses:list=[]
    for business in businesses:
        find_a=business.find_element(By.TAG_NAME,"a")
        url = find_a.get_attribute('href')
        # print(url)
        web_driver.open_new_tab()
        web_driver.open_url(url=url)
        time.sleep(2)
        page_source = web_driver.page_source()
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract information
        info_section = soup.find('div', class_='m6QErb XiKgde')
        details = {}
        name_tag = soup.find('h1', class_='DUwDvf lfPIob')
        name = name_tag.text.strip() if name_tag else "Name not found"
        # Extract rating and reviews
        rating_section = soup.find('div', class_='fontBodyMedium dmRWX')

        if rating_section:
            # Extract the rating
            rating_span = rating_section.find('span', {'aria-hidden': 'true'})
            rating = rating_span.text.strip() if rating_span else "Rating not found"

            # Extract the number of reviews
            reviews_span = rating_section.find('span', {'aria-label': lambda x: x and 'reviews' in x})
            reviews = reviews_span['aria-label'] if reviews_span else "Reviews not found"
        else:
            rating = 0
            reviews = 0
        details.update({"business_name":name,"rating":rating,"reviews":reviews})
        if info_section:
            # Extract address
            address_button = info_section.find('button', {'data-item-id': 'address'})
            if address_button:
                details['Address'] = address_button.find('div', class_='Io6YTe').text.strip()

            # Extract website
            website_link = info_section.find('a', {'data-item-id': 'authority'})
            if website_link:
                details['Website'] = website_link.get('href')

            # Extract phone number
            phone_button = info_section.find('button', {'data-item-id': lambda x: x and x.startswith('phone:')})
            if phone_button:
                details['Phone'] = phone_button.find('div', class_='Io6YTe').text.strip()

            # Extract plus code
            plus_code_button = info_section.find('button', {'data-item-id': 'oloc'})
            if plus_code_button:
                details['Plus Code'] = plus_code_button.find('div', class_='Io6YTe').text.strip()
        all_businesses.append(details)
        # Print the extracted details
        # for key, value in details.items():
        #     print(f"{key}: {value}")

        web_driver.close_tab()
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_businesses)

    # Sort the DataFrame by 'Rating' in descending order
    df_sorted = df.sort_values(by="rating", ascending=False)

    # Save the sorted DataFrame to a CSV file
    csv_file = "map.csv"
    df_sorted.to_csv(csv_file, index=False)

    # Display the DataFrame
    # print(df_sorted)
    print(f"Data has been saved to {csv_file}")
    time.sleep(10)


if __name__ == "__main__":
    search = "college near me"
    gmap_scraper(search)
