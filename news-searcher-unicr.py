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


# News/Publications Search- Unicredit

# Bank specific vars
bank = "unicredit"
bank_news_url = "https://www.unicreditbulbank.bg/bg/za-nas/media/novini/"
# Outputs fpaths
articles_output_fpath = f"outputs/search_results_articles_{bank}.csv"


# Open chrome driver
driver = webdriver.Chrome(options = set_chrome_options())

# Navigate to news page
driver.get(bank_news_url)
time.sleep(3)

#  Search in media publications with keywords

# Noting alt search paths
# "/html/body/div[2]/div/div[1]/div/div/form/fieldset/div/div[2]/input"
# search_btn = driver.find_element(By.CLASS_NAME, "btn btn-primary search-btn")
# "//*[@id="news-search-form"]/input"

article_titles = []
article_summaries = []
article_dates = []
article_hrefs = []
keyword_list = []

for i in range(0,len(keywords)):

    keyword = keywords[i]

    # Log keyword being used
    print(f"Keyword -> {keyword}----------------------------------")

    # Identify webelements for searching (each loop to avoid stale state)
    keyword_search_webel = driver.find_element(By.XPATH, "//*[@id='id_keywords']")
    #//*[@id="id_keywords"]
    if i == 0:
        search_btn = driver.find_element(By.XPATH, "//*[@id='news-search-form']/input")
    else:
        search_btn = driver.find_element(By.XPATH, "//*[@id='news-search-form']/span/button")
        keyword_search_webel.clear()

    # Input keyword
    keyword_search_webel.click()
    keyword_search_webel.send_keys(keyword)
    # Search
    search_btn.click()

    # Allow time for the search
    time.sleep(5)


    # Check out visible articles
    visible_articles = driver.find_elements(By.XPATH, "//*[@id='news_list']/div")
    # Returns 0 if no hits
    n_visible_articles = len(visible_articles)

    #n_articles = 0

    # Check if all articles visible, if not get total
    try:
        # Identify show more webelement
        show_more_webel = driver.find_element(By.XPATH, "//*[@id='main-id']/div[2]/div/div[2]/p/a")
        show_more_UB_webel = driver.find_element(By.XPATH, '//*[@id="main-id"]/div[2]/div/div[2]/p/a/span[2]')
        all_visible = False
    except Exception as e:
        all_visible = True
        #print("Keyword generated too large number of hits.")

    if not all_visible:
        # Identify number of all articles
        n_hidden_articles = int(show_more_UB_webel.get_attribute("innerHTML"))
        n_articles = n_visible_articles + n_hidden_articles

        if n_articles > 1000:
            # too many hits, bogus search
            print(f"Number of articles found -> {n_articles}----------------------------------")
            print("NOTE!!! Too many hits, search engine issue assumed!!!")
            continue

        # Identify n times to click on show more
        n_click_show_more = math.ceil(n_hidden_articles/10)

        for i in range(0, n_click_show_more):
            # Relocate show more button
            show_more_webel = driver.find_element(By.XPATH, "//*[@id='main-id']/div[2]/div/div[2]/p/a")
            # Scroll to bottom to avoid click intercept error with cookies bar
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # Click to show more
            show_more_webel.click()
            # Wait to give time to load
            time.sleep(11)
    else:
        # Only artivles are visible ones
        n_articles = len(visible_articles)


    print(f"Number of articles found -> {n_articles}----------------------------------")


    # //*[@id="news_list"]/div[1]/div/div[2]/h2/a
    # //*[@id="news_list"]/div[2]/div/div[2]/h2/a
    # //*[@id="news_list"]/div[17]/div/div/h2/a
    # //*[@id="news_list"]/div[18]/div/div/h2/a

    for i in range(1, n_articles+1):

        # Check if article is with pic or not (extra div container when with pic)
        article_webel_n_divs = len(driver.find_elements(By.XPATH, f"//*[@id='news_list']/div[{i}]/div/div"))
        # Set xpath to scrape article info accordingly
        if article_webel_n_divs == 2:
            # Article with image and text summary
            title_xpath = f"//*[@id='news_list']/div[{i}]/div/div[2]/h2/a"
            date_xpath = f"//*[@id='news_list']/div[{i}]/div/div[2]/div[2]/time"
            summary_xpath = f"//*[@id='news_list']/div[{i}]/div/div[2]/p"
        elif article_webel_n_divs == 1:
            #Article with text content summary only
            title_xpath = f"//*[@id='news_list']/div[{i}]/div/div/h2/a"
            date_xpath = f"//*[@id='news_list']/div[{i}]/div/div/div[2]/time"
            summary_xpath = f"//*[@id='news_list']/div[{i}]/div/div/p"

        # Collect keyword, title, href, date  match for titles
        article_title = driver.find_element(By.XPATH, title_xpath).get_attribute("innerHTML")
        article_href = driver.find_element(By.XPATH, title_xpath).get_attribute("href")
        date = driver.find_element(By.XPATH, date_xpath).get_attribute("datetime")
        summary = driver.find_element(By.XPATH, summary_xpath).get_attribute("innerHTML")

        # Add to lists to use later
        article_titles.append(article_title)
        article_hrefs.append(article_href)
        article_dates.append(date)
        article_summaries.append(summary)
        keyword_list.append(keyword)


# Create df with keyword-title-link for publications
colnames = ["keyword", "title", "summary", "date", "href"]
articles_df = pd.DataFrame(list(zip(keyword_list, article_titles, article_summaries, article_dates, article_hrefs)),
                            columns = colnames)
articles_df.to_csv(articles_output_fpath)


# Visible articles
# XPATH
# href of an article (first) '/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div/div[2]/h2/a'
# //*[@id="news_list"]/div[1]/div/div[2]/h2/a
# href of an article (second) '/html/body/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/h2/a'
# //*[@id="news_list"]/div[2]/div/div[2]/h2/a
# href of an article (last)   '/html/body/div[2]/div/div[2]/div/div[1]/div[9]/div/div[2]/h2/a'
# //*[@id="news_list"]/div[2]/div/div[9]/h2/a

# href of grid with articles '/html/body/div[2]/div/div[2]/div/div[1]'
# //*[@id="news_list"]

time.sleep(3)
driver.get_screenshot_as_file("screenshots/test.png")

driver.quit()

