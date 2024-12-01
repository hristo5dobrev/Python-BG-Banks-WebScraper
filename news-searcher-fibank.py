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
bank = "fibank"
bank_news_url = "https://www.fibank.bg/bg/za-nas/novini/novini"
# Outputs fpaths
results_output_fpath = f"outputs/search_results_{bank}.csv"

# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to news page
driver.get(bank_news_url)
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
                                                
    # Open bar to enable search box
    search_icon = driver.find_element(By.XPATH, "/html/body/div/header/div[1]/div/div[2]/ul/li[7]/a/i")
    time.sleep(2)
    search_icon.click()
    time.sleep(2)
    

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "//*[@id='header_search_id']")
    #search_btn = driver.find_element(By.XPATH, "/html/body/div/header/div[2]/div/div[2]/div/form/button[2]")

    # Input keyword
    keyword_search_webel.click()
    keyword_search_webel.send_keys(keyword)
    # Search
    keyword_search_webel.send_keys(Keys.RETURN)

    # Allow time for the search
    time.sleep(3)

    # Get number of hits
    n_results = driver.find_element(By.XPATH, "/html/body/div/main/section[1]/div/div[1]/div/div[2]/p")
    n_results = n_results.get_attribute("innerHTML")
    n_results = re.search(r'\d+', n_results)
    n_results = n_results.group()
    n_results = int(n_results)

    if n_results == 0:
        continue

    print(f"Number of search results found -> {n_results}----------------------------------")


    for i in range(1, n_results+1):

        # Set xpath to access result info accordingly
        category_xpath = f"/html/body/div/main/section[1]/div/div[2]/ul/li[{i}]/div[1]/h3"
        title_xpath = f"/html/body/div/main/section[1]/div/div[2]/ul/li[{i}]/div[1]/h2/a"
        summary_xpath = f"/html/body/div/main/section[1]/div/div[2]/ul/li[{i}]/div[1]/p"

        # Locate webels
        category_webel = driver.find_element(By.XPATH, category_xpath)
        title_webel = driver.find_element(By.XPATH, title_xpath)
        summary_webel = driver.find_element(By.XPATH, summary_xpath)

        # Get title, category, href, summary
        category = category_webel.get_attribute("innerHTML").lower()
        title = title_webel.get_attribute("innerHTML")
        result_href = title_webel.get_attribute("href")
        summary = summary_webel.get_attribute("innerHTML")
        date = "NA"

        # Check if link still live
        search_url = driver.current_url
        title_webel.click()
        time.sleep(3)
        current_url = driver.current_url

        # If no change in URL skip result as no longer available
        if current_url == search_url:
            continue
        
        # Get date of publishing (if news, else not available)
        if category == "news":
            date = driver.find_element(By.XPATH, "/html/body/div/main/header/div/time").get_attribute("innerHTML")

        # Go back to search page
        driver.back()
        time.sleep(2)

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

