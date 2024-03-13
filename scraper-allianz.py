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
from key_vars import download_filepath, earliest_report_year, final_report_year, pdf_links_fpath


# Scrape- Unicredit Bulbank

# Bank specific vars
bank = "allianz"
bank_url = "https://www.allianz.bg/bg_BG/individuals/banking/tariffs-and-documents/bank-documents.html#"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

print("Scraping Allianz reports")

# Go to starting page
driver.get(bank_url)
time.sleep(3)
# Screenshot homepage to track progress
driver.get_screenshot_as_file("screenshots/startPage.png")

# Reject cookies
reject_cookies = driver.find_element(By.XPATH, "//*[@id='onetrust-reject-all-handler']")
reject_cookies.click()

# Go to fin reports
fin_reports_page = driver.find_element(By.XPATH, "//*[@id='TabVerticalNegative5123355035']/div")
fin_reports_page.click()

# Pick up latest report year (first el of chosen class)
final_report_year_website = driver.find_element(By.XPATH, "//*[@id='ContentVerticalNegative5123355035']/div[2]/div/div/div/div[1]/button/span").get_attribute("innerHTML")
final_report_year_website = int(final_report_year_website)

if final_report_year > final_report_year_website:
    final_report_year = final_report_year_website
    print(f"NOTE! Final report year requested is not available on the bank's website, using latest available- {final_report_year}")


# Define empty lists to fill with pdf information
pdf_file_links = []
pdf_file_names = []

# Note already downloaded files to avoid duplicates
downloaded_files = os.listdir(download_filepath)

# Download all pdf reports for each year in specified range

# Download all pdf reports for each year in specified range
for reporting_year_i in reversed(list(range(earliest_report_year, final_report_year+1))):
    # Print out year being processed
    print(f"Parsing Year ---> {reporting_year_i}")

    # Set up number of reports wrt year
    if reporting_year_i in range(2021,2022+1):
        reports_index_li = [1,3]
    elif reporting_year_i == 2020:
        reports_index_li = [1,4]
    elif reporting_year_i in range(2018,2019+1):
        reports_index_li = [1,2]
    elif reporting_year_i in range(2016,2017+1):
        reports_index_li = [1,2,3]
    elif reporting_year_i < 2016:
        reports_index_li = [2,3,5,6,8,9,11,12,14,15,17,19,21]
        reporting_year_i = ""

    # Loop through all the reports
    for i in reports_index_li:
        
        # Print out report number/index
        print(f"Parsing Report ---> {i}")

        # Handle special/weird case for 2020
        if reporting_year_i == 2020:
            # Locate href
            href_xpath = f"//*[@id='content{reporting_year_i}']/div/div/div/div[{i}]/a"
             # Locate name
            name_xpath = f"//*[@id='content{reporting_year_i}']/div/div/div/div[{i}]/a/span[2]"
        else:
            # Locate href
            href_xpath = f"//*[@id='content{reporting_year_i}']/div/div/div/p[{i}]/a"
             # Locate name
            name_xpath = f"//*[@id='content{reporting_year_i}']/div/div/div/p[{i}]/a/span[2]"


        # Take name and href
        pdf_url = driver.find_element(By.XPATH, href_xpath).get_attribute("href") 
        pdf_name = driver.find_element(By.XPATH, name_xpath).get_attribute("innerHTML")

        # Log pdf name
        print(pdf_name)
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

    # if iter done for year before 2016 it'd have covered full archive already
    if reporting_year_i == "":
        break


# Save pdf files' links for later use
# First read in old table and then add new entries
bank_col_vals = [bank] * len(pdf_file_names)
pdf_downloads_info_old = pd.read_csv(pdf_links_fpath)
pdf_downloads_info_new = pd.DataFrame(list(zip(bank_col_vals, pdf_file_names, pdf_file_links)), columns = ["bank", "filename", "href"])
pdf_downloads_info = pd.concat([pdf_downloads_info_old, pdf_downloads_info_new], ignore_index=True)
pdf_downloads_info.to_csv(pdf_links_fpath, index = False)

# Quit driver
print(driver.current_url)
driver.quit()
