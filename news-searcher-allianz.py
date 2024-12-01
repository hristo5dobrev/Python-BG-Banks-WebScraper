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
bank = "allianz"
bank_media_url = "https://www.allianz.bg/bg_BG/individuals.html"
# Outputs fpaths
results_output_fpath = f"outputs/search_results_{bank}.csv"

# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to news page
driver.get(bank_media_url)
time.sleep(3)

# Reject cookies
reject_cookies = driver.find_element(By.XPATH, "//*[@id='onetrust-reject-all-handler']")
reject_cookies.click()
time.sleep(1)

# Open Search bar
search_open = driver.find_element(By.XPATH, "//*[@id='onemarketing-search-opener']/span[2]")
search_open.click()
time.sleep(1)


# Arrays to store data between iterations
result_titles = []
result_dates = []
result_hrefs = []
keyword_list = []
result_categories = []
result_summaries = []


#  Search keywords
for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")
    

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div/div[2]/header/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div[2]/input")
    search_submit = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div/div[2]/header/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div/div/div/div[3]/button[1]")

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

    # Get number of pages
    n_results_pages = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[3]/div[3]/div/div/div/div[2]/nav/div/span[3]")
    n_results_pages = n_results_pages.get_attribute("innerHTML")
    n_results_pages = int(n_results_pages)

    # If no results- next keyword
    if n_results_pages == 0:
        continue
    
    # Get number of hits
    n_results = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div[1]/div[2]/p")
    n_results = n_results.get_attribute("innerHTML")
    n_results = re.findall(r'\d+', n_results)
    n_results = int(n_results[0])

    # Get number of results on page
    results_first_page = len(driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div"))

    print(f"Number of search results found -> {n_results} (in {n_results_pages} pages)----------------------------------")

    # Loop pages
    for page_i in range(1, n_results_pages+1):

        if page_i > 1:
            # Go to next page
            next_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[3]/div[3]/div/div/div/div[2]/nav/a[2]/span")
            next_btn.click()
            time.sleep(3)

            # Get results on page
            results_on_page = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div")
            results_on_page = len(results_on_page)
        elif page_i == 1:
            results_on_page = results_first_page


        # Loop results
        for i in range(1, results_on_page+1):

            # Set default xpath to access result info accordingly
            category_xpath = f"/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[{i}]/div/div/div/div/nav/ul/li[2]/a"
            title_xpath = f"/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[{i}]/div/div/div/div/h5/a"
            summary_xpath = f"/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[{i}]/div/div/div/div/p"

            # Find webelements
            category_webel = driver.find_element(By.XPATH, category_xpath)
            title_webel = driver.find_element(By.XPATH, title_xpath)
            summary_webel = driver.find_element(By.XPATH, summary_xpath)

            # Get values
            result_href = title_webel.get_attribute("href")
            category = category_webel.get_attribute("innerHTML")
            title = title_webel.get_attribute("innerHTML")
            summary = summary_webel.get_attribute("innerHTML")
            date = "NA"
            

            # Add to lists to use later
            result_titles.append(title)
            result_hrefs.append(result_href)
            result_dates.append(date)
            result_summaries.append(summary)
            result_categories.append(category)
            keyword_list.append(keyword)


# Create df with keyword-title-link for publications
colnames = ["keyword", "title", "category", "summary", "date", "href"]
results_df = pd.DataFrame(list(zip(keyword_list, result_titles, result_categories, result_summaries, result_dates, result_hrefs)),
                            columns = colnames)
results_df.to_csv(results_output_fpath)


driver.get_screenshot_as_file("screenshots/test.png")
driver.quit()

