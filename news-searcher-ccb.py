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
bank = "ccb"
bank_media_url = "https://www.ccbank.bg/bg/search?term="
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
result_categories = []
result_summaries = []


for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")
    

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "/html/body/div/main/div/div/div/form/div/input")
    search_submit = driver.find_element(By.XPATH, "/html/body/div/main/div/div/div/form/div/button")

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

    # Check if any results- if none next iter
    n_results_check = driver.find_elements(By.XPATH, "/html/body/div/main/div/div/div/form/div[2]/span[1]/span")
    if len(n_results_check) == 0:
        continue

    # Get number of hits
    n_results = driver.find_element(By.XPATH, "/html/body/div/main/div/div/div/form/div[2]/span[1]/span")
    n_results = n_results.get_attribute("innerHTML")

    # Get number of pages
    n_results_pages = driver.find_element(By.XPATH, "/html/body/div/main/div/div/div/form/div[2]/span[2]")
    n_results_pages = n_results_pages.get_attribute("innerHTML")
    n_results_pages = re.findall(r'\d+', n_results_pages)
    n_results_pages = int(n_results_pages[len(n_results_pages)-1])

    # Get number of results on page
    # Assume results per page wrt first page (apart fromn last page)
    results_first_page = driver.find_elements(By.CLASS_NAME, "blocks-list__item")
    results_first_page = len(results_first_page)

    print(f"Number of search results found -> {n_results}----------------------------------")

    # Loop pages
    for page_i in range(1, n_results_pages+1):

        if page_i > 1:
            # Go to next page
            next_btn = driver.find_element(By.CLASS_NAME, "paginator__btn--next")
            next_btn.click()
            time.sleep(3)

            # Get results on page
            results_on_page = driver.find_elements(By.CLASS_NAME, "blocks-list__item")
            results_on_page = len(results_on_page)
        elif page_i == 1:
            results_on_page = results_first_page


        # Loop results
        for i in range(1, results_on_page+1):

            # Set default xpath to access result info accordingly
            href_xpath = f"/html/body/div/main/div/div/div/ul/li[{i}]/a"
            category_xpath = f"/html/body/div/main/div/div/div/ul/li[{i}]/a/span"
            title_xpath = f"/html/body/div/main/div/div/div/ul/li[{i}]/a/strong"
            summary_xpath = f"/html/body/div/main/div/div/div/ul/li[{i}]/a/div/p"

            # Find webelements
            href_xpath_webel = driver.find_element(By.XPATH, href_xpath)
            category_webel = driver.find_element(By.XPATH, category_xpath)
            title_webel = driver.find_element(By.XPATH, title_xpath)
            summary_webel = driver.find_element(By.XPATH, summary_xpath)

            # Get values
            result_href = href_xpath_webel.get_attribute("href")
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

