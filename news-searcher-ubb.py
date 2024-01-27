# Core pkgs
import math
import time
import pandas as pd
import os
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


# News/Publications Search- UBB

# Bank specific vars
bank = "ubb"
# NOTE- we will use search box in website's menu for efficiency as no keyword searchbox for news only
# the aforementioned searchbox applies an even wider search than solely news
bank_news_url = "https://www.ubb.bg/en/news"
# Outputs fpaths
results_output_fpath = f"outputs/search_results_{bank}.csv"

# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to news page
driver.get(bank_news_url)
time.sleep(3)

# Decline cookies
cookies_btn = driver.find_element(By.XPATH, "//*[@id='CybotCookiebotDialogBodyButtonDecline']")
cookies_btn.click()
time.sleep(1)

#  Search in media publications with keywords

result_titles = []
result_dates = []
result_hrefs = []
keyword_list = []


for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")
                                                
    # Open nav bar to enable search box
    if i == 0:
        nav_btn = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div/div/div[2]/div/div[1]")
    else:
        nav_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div/div[3]")
        
    nav_btn.click()

    time.sleep(2)

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "//*[@id='search-input']")
    search_btn = driver.find_element(By.XPATH, "//*/button[@type='submit']/img")
    #search_btn = driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div/div[2]/div/form/div/div/button/img")
    
    # #//*[@id="id_keywords"]
    # if i == 0:
    #     search_btn = driver.find_element(By.XPATH, "//*[@id='news-search-form']/input")
    # else:
    #     search_btn = driver.find_element(By.XPATH, "//*[@id='news-search-form']/span/button")
    #     keyword_search_webel.clear()

    # Input keyword
    keyword_search_webel.click()
    keyword_search_webel.send_keys(keyword)
    # Search
    search_btn.click()

    # Allow time for the search
    time.sleep(7)

    # Get number of hits
    n_results = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/p")
    n_results = n_results.get_attribute("innerHTML")
    n_results = n_results[len(n_results)-1]
    n_results = int(n_results)

    if n_results == 0:
        continue

    print(f"Number of search results found -> {n_results}----------------------------------")


    for i in range(1, n_results+1):

        # Set xpath to access result info accordingly
        category_xpath = f"/html/body/div[3]/div[2]/div/div[2]/div/div/div[{i}]/a[1]"
        title_xpath = f"/html/body/div[3]/div[2]/div/div[2]/div/div/div[{i}]/a[2]"

        # Locate webels
        category_webel = driver.find_element(By.XPATH, category_xpath)
        title_webel = driver.find_element(By.XPATH, title_xpath)

        # Get title, category, href, date
        category = category_webel.get_attribute("innerHTML").lower()
        title = title_webel.get_attribute("innerHTML")
        result_href = title_webel.get_attribute("href")
        date = "NA"

        # Exclude result if obviously wrong (Office Move Notif)
        if "address change" in title:
            continue

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
            date = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div/div[2]/p/span").get_attribute("innerHTML")

        # Go back to search page
        driver.back()
        time.sleep(2)

        # Add to lists to use later
        result_titles.append(result_href)
        result_hrefs.append(result_href)
        result_dates.append(date)
        keyword_list.append(keyword)


# Create df with keyword-title-link for publications
colnames = ["keyword", "title", "summary", "date", "href"]
results_df = pd.DataFrame(list(zip(keyword_list, result_titles, result_dates, result_hrefs)),
                            columns = colnames)
results_df.to_csv(results_output_fpath)


driver.get_screenshot_as_file("screenshots/test.png")
driver.quit()

