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


# News/Publications Search- UBB

# Bank specific vars
bank = "dsk"
bank_media_url = "https://dskbank.bg/"
# Outputs fpaths
results_output_fpath = f"outputs/search_results_{bank}.csv"

# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to bank web page
driver.get(bank_media_url)
driver.maximize_window()
time.sleep(5)

# Handle cookies pop up
cookies_btn = driver.find_element(By.XPATH, "//*[@id='CybotCookiebotDialogBodyButtonAcceptAll']")
cookies_btn.click()
# Handle add pop up
close_add = driver.find_element(By.XPATH, "//*[@id='popup-banner-modal']/div/span")
close_add.click()

# Search keywords
result_titles = []
result_dates = []
result_hrefs = []
result_cats = []
keyword_list = []
result_summaries = []

for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")
    

    # Identify webelements for searching (each loop to avoid stale state)
    if i == 0:
        keyword_search_webel = driver.find_element(By.XPATH, "/html/body/div[4]/header/div[1]/div[1]/ul/li[3]/button")
        input_webel = driver.find_element(By.XPATH, "/html/body/div[4]/header/div[1]/div[1]/ul/li[3]/div/div/div/div/div/div/div/input")
        search_submit = driver.find_element(By.XPATH, "/html/body/div[4]/header/div[1]/div[1]/ul/li[3]/div/div/div/div/div/button")
    else:
        keyword_search_webel = driver.find_element(By.XPATH, "/html/body/div[2]/header/div[1]/div[1]/ul/li[3]/button")
        input_webel = driver.find_element(By.XPATH, "/html/body/div[2]/header/div[1]/div[1]/ul/li[3]/div/div/div/div/div/div/div/input")
        search_submit = driver.find_element(By.XPATH, "/html/body/div[2]/header/div[1]/div[1]/ul/li[3]/div/div/div/div/div/button")

    # Input keyword
    keyword_search_webel.click()
    time.sleep(1)
    input_webel.click()
    input_webel.send_keys(keyword)
    # Search
    search_submit.click()

    # Allow time for the search
    time.sleep(3)

    # Get number of hits
    n_results = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[2]/div/section[1]/div[1]/div[1]/h3").get_attribute("innerHTML")
    n_results = re.search(r'\d+', n_results)
    n_results = n_results.group()

    # Get pagination data
    pagination_bar_webels = driver.find_elements(By.XPATH, "/html/body/div[2]/main/div[2]/div/section[1]/div[2]/div/div/ul/li")
    n_results_pages = len(pagination_bar_webels)

    print(f"Number of search results found -> {n_results}----------------------------------")

    # Loop pages
    for page_i in range(0, n_results_pages):

        if page_i > 0:
            # Go to next page
            pagination_bar_webels = driver.find_elements(By.XPATH, "/html/body/div[2]/main/div[2]/div/section[1]/div[2]/div/div/ul/li")
            driver.execute_script("arguments[0].scrollIntoView();", pagination_bar_webels[page_i])
            time.sleep(1)
            pagination_bar_webels[page_i].click()
            time.sleep(3)

        # Get results on page
        results_on_page = driver.find_elements(By.CLASS_NAME, "search-results__item")
        n_results_on_page = len(results_on_page)


        # Loop through results
        for i in range(0, n_results_on_page):

            # Set default xpath to access result info accordingly
            category_classname = "search__label"
            title_classname = "news__title"
            summary_classname = "news__text"
            href_classname = "news__link"

            # Handle category
            category_webel = results_on_page[i].find_element(By.CLASS_NAME, category_classname)
            category = category_webel.get_attribute("innerHTML")

            # Date not available
            date = "NA"

            # Handle href
            href_webel = results_on_page[i].find_elements(By.CLASS_NAME, href_classname)
            if len(href_webel) > 0:
                href_webel = results_on_page[i].find_element(By.CLASS_NAME, href_classname)
                result_href = href_webel.get_attribute("href")
            else:
                result_href = "NA"
            
            # Handle title
            title_webel = results_on_page[i].find_element(By.CLASS_NAME, title_classname)
            title_inner = title_webel.get_attribute("innerHTML")
            tag_a = "</a>"
            if tag_a in title_inner:
                title_webel = title_webel.find_element(By.TAG_NAME, "a")
                title = title_webel.get_attribute("innerHTML")
            else:
                title = title_inner

            # Check if wizz air article- many hits for AI search- filter out
            check_string = 'Wizz <strong class="sfHighlight">Air</strong>'
            if check_string.lower() in title.lower():
                continue

            # Handle summary as not always available
            summary_webel = results_on_page[i].find_element(By.CLASS_NAME, summary_classname)
            summary_inner = summary_webel.get_attribute("innerHTML")
            if summary_inner != "":
                p_tag = "</p>"
                if p_tag in summary_inner:
                    summary_webel = summary_webel.find_element(By.TAG_NAME, "p")
                    summary = summary_webel.get_attribute("innerHTML")
                else:
                    summary = summary_inner
            else:
                summary = "NA"
            

            # Add to lists to use later
            result_titles.append(title)
            result_hrefs.append(result_href)
            result_cats.append(category)
            result_dates.append(date)
            result_summaries.append(summary)
            keyword_list.append(keyword)


# Create df with keyword-title-link for publications
colnames = ["keyword", "category", "title", "summary", "date", "href"]
results_df = pd.DataFrame(list(zip(keyword_list, result_cats, result_titles, result_summaries, result_dates, result_hrefs)),
                            columns = colnames)
results_df.to_csv(results_output_fpath)


driver.get_screenshot_as_file("screenshots/test.png")
driver.quit()

