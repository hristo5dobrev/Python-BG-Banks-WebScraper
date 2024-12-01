# Core pkgs
import math
import time
import pandas as pd
import re
# Browser/HTML navigating pkgs and f-s
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
#from selenium.common.exceptions import ElementClickInterceptedException
# User defined function and vars
from supporting_functions import set_chrome_options
from key_vars import keywords, earliest_report_year, final_report_year


# Bank specific vars
bank = "postbank"
bank_media_url = "https://mediacenter.postbank.bg"
# Outputs fpaths
results_output_fpath = f"outputs/search_results_{bank}.csv"

# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to news page
driver.get(bank_media_url)
time.sleep(3)

#  Search keywords

result_titles = []
result_dates = []
result_hrefs = []
keyword_list = []
result_summaries = []


for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")
    

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "//*[@id='s']")
    search_submit = driver.find_element(By.XPATH, "//*[@id='searchsubmit']")

    # Input keyword
    keyword_search_webel.click()
    if i > 0:
        keyword_search_webel.clear()
        time.sleep(2)
    keyword_search_webel.send_keys(keyword)
    # Search
    search_submit.click()

    # Allow time for the search
    time.sleep(3)

    # Get number of hits

    # Get pagination data
    n_results_pages_raw = driver.find_elements(By.CLASS_NAME, "wp-paginate")
    # Get number of results on page
    # Assume results per page wrt first page (apart fromn last page)
    results_first_page = driver.find_elements(By.CLASS_NAME, "news")
    results_first_page = len(results_first_page)

    # Determine number of pages
    # Pagination webel shows only for 2+ pages
    if len(n_results_pages_raw) > 0:
        # Parse innerHTML to get number of pages
        result_pages_html_content = n_results_pages_raw[0].get_attribute('innerHTML')
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(result_pages_html_content, 'html.parser')
        # Find all li elements
        li_elements = soup.find_all('li')
        # Subtract 2 as there is a title element (i.e. empty) and next page element
        n_results_pages = len(li_elements) - 2
    elif len(n_results_pages_raw) == 0 and results_first_page > 0:
        n_results_pages = 1
    else:
        n_results_pages = 0 

    # If no hits found list is empty- continue
    if n_results_pages == 0 and results_first_page == 0:
        continue

    print(f"Number of search results found -> Up To {n_results_pages}pages * {results_first_page}results----------------------------------")

    # Loop pages
    for page_i in range(1, n_results_pages+1):

        if page_i > 1:
            # Go to next page
            next_btn = driver.find_element(By.CLASS_NAME, "next")
            next_btn.click()
            time.sleep(3)

            # Get results on page
            results_on_page = driver.find_elements(By.CLASS_NAME, "news")
            results_on_page = len(results_on_page)
        elif page_i == 1:
            results_on_page = results_first_page


        # Loop results
        for i in range(1, results_on_page+1):

            # Set default xpath to access result info accordingly
            title_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div[2]/h2/a"
            summary_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div[2]/p"
            date_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div[2]/div/div[1]"

            # Handle special cases
            summary_test = driver.find_elements(By.XPATH, summary_xpath)
            title_test = driver.find_elements(By.XPATH, title_xpath)

            
            if len(title_test) == 0:
                # Get summary
                summary_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div"
                summary_webel = driver.find_element(By.XPATH, summary_xpath)
                summary = summary_webel.text
                # No title available
                title = "NA"
                # Get href
                href_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div/div/div[2]/a"
                href_webel = driver.find_element(By.XPATH, href_xpath)
                result_href = href_webel.get_attribute("href")
                # Get date
                date_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div/div/div[1]"
                date_webel = driver.find_element(By.XPATH, date_xpath)
                date = date_webel.get_attribute("innerHTML")

            elif len(summary_test) == 0 and len(title_test) != 0:
                # Handle summary
                summary_xpath = f"//*[@id='searchbar']/div[1]/div[{i}]/div[2]"
                summary_webel = driver.find_element(By.XPATH, summary_xpath)
                summary = summary_webel.text

                # Handle other info- title, href, date
                title_webel = driver.find_element(By.XPATH, title_xpath)
                date_webel = driver.find_element(By.XPATH, date_xpath)
                title = title_webel.get_attribute("innerHTML")
                result_href = title_webel.get_attribute("href")
                date = date_webel.get_attribute("innerHTML")

            else:
                # Find webelements
                summary_webel = driver.find_element(By.XPATH, summary_xpath)
                title_webel = driver.find_element(By.XPATH, title_xpath)
                date_webel = driver.find_element(By.XPATH, date_xpath)
                # Get values
                title = title_webel.get_attribute("innerHTML")
                result_href = title_webel.get_attribute("href")
                summary = summary_webel.get_attribute("innerHTML")
                date = date_webel.get_attribute("innerHTML")
            

            # Add to lists to use later
            result_titles.append(title)
            result_hrefs.append(result_href)
            result_dates.append(date)
            result_summaries.append(summary)
            keyword_list.append(keyword)


# Create df with keyword-title-link for publications
colnames = ["keyword", "title", "summary", "date", "href"]
results_df = pd.DataFrame(list(zip(keyword_list, result_titles, result_summaries, result_dates, result_hrefs)),
                            columns = colnames)
results_df.to_csv(results_output_fpath)


driver.get_screenshot_as_file("screenshots/test.png")
driver.quit()

