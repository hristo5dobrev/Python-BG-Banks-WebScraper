# Core pkgs
import requests
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
from key_vars import desired_text_results_page, download_filepath, unicredit_url, earliest_report_year, final_report_year


# Scrape- Unicredit Bulbank

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

# Go to unicredit homepage
driver.get(unicredit_url)
time.sleep(3)

# Screenshot homepage to track progress
driver.get_screenshot_as_file("homePage.png")

# Check page language
language_btn_li = driver.find_elements(By.CLASS_NAME, "nav__main__items__lang")
language_btn_txt = language_btn_li[0].get_attribute("textContent").strip()
if str.upper(language_btn_txt) != "ENGLISH":
    raise Exception("Unexpected unicredit webpage language setting. Make sure starting link is correct- entering website in bulgarian.")

# Go to about us pages
about_us_btn = driver.find_element(By.XPATH, "//a[contains(@href, '/bg/za-nas/')]")
about_us_url = about_us_btn.get_attribute("href")
driver.get(about_us_url)

# Take screenshot- for troubleshooting
driver.get_screenshot_as_file("aboutUsPage.png")
time.sleep(3)

# Go to results- financial reports
element = driver.find_element(By.XPATH, f'//a[contains(text(), "{desired_text_results_page}")]')
element_href = element.get_attribute("href") + "finansovi-otcheti"
driver.get(element_href)
time.sleep(3)

# Define empty lists to fill with pdf information
pdf_file_links = []
pdf_file_names = []

# Note already downloaded files to avoid duplicates
downloaded_files = os.listdir(download_filepath)

# Download all pdf reports for each year in specified range
for reporting_year_i in range(earliest_report_year, final_report_year):
    # Report XPATHs note below
    #//*[@id="2021-id"]/div/div/ul/li/a
    # //*[@id="2018-id"]/div/div/ul
    # //*[@id="2018-id"]/div/div/ul/li[2]/a
    # //*[@id="2018-id"]/div/div/ul/li[1]/a
    # Print out year being processed
    print(f"Parsing Year ---> {reporting_year_i}")

    # Use find_elements to see if there are any for given XPATH- specifically wrt given year
    check_reports_exist = driver.find_elements(By.XPATH, f"//*[@id='{reporting_year_i}-id']/div/div/ul")
    if len(check_reports_exist) == 0:
        continue

    # Check out number of reports for given year
    n_reports = driver.find_element(By.XPATH, f"//*[@id='{reporting_year_i}-id']/div/div/ul")
    n_reports = n_reports.find_elements(By.TAG_NAME, "li")
    n_reports = len(n_reports)

    # Get all reports for given year
    for i in range(1, n_reports+1):
        
        # Print out report number/index
        print(f"Parsing Report ---> {i}")

        # Find pdf report element
        fin_report_pdf_element = driver.find_element(By.XPATH, f"//*[@id='{reporting_year_i}-id']/div/div/ul/li[{i}]/a")
        print(fin_report_pdf_element.get_attribute("textContent"))

        # Get report's pdf details
        pdf_url = fin_report_pdf_element.get_attribute("href")
        pdf_name = fin_report_pdf_element.get_attribute("title")
        # Make sure no / are in pdf name
        pdf_name = pdf_name.replace("/", "_")

        # Check if doc has been downloaded
        pdf_name_check = pdf_name+".pdf"
        if pdf_name_check in downloaded_files:
            continue

        # Store pdf links to provide them later
        pdf_file_links.append(pdf_url)
        pdf_file_names.append(f"{pdf_name}.pdf")

        # Download pdf
        # Define headers dict with user-agent as needed by website
        headers = {"user-agent": "agent"}
        # Get response and write pdf locally
        response = requests.get(pdf_url, headers=headers, timeout=45)
        print(response.status_code)
        if response.status_code == 200:
            with open(f"{download_filepath}/{pdf_name}.pdf", "wb") as pdf_file:
                pdf_file.write(response.content)
        
        time.sleep(3)
        print("Report downloaded, link and name noted;")

# Save pdf files' links for later use
# First read in old table and then add new entries
pdf_downloads_info_old = pd.read_csv("pdf_downloads_links.csv")
pdf_downloads_info_new = pd.DataFrame(list(zip(pdf_file_names, pdf_file_links)), columns = ["filename", "href"])
pdf_downloads_info = pd.concat([pdf_downloads_info_old, pdf_downloads_info_new], ignore_index=True)
pdf_downloads_info.to_csv("pdf_downloads_links.csv", index = False)

# Quit driver
print(driver.current_url)
driver.quit()
