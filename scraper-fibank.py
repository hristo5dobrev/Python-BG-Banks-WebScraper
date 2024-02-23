# Core pkgs
import requests
import time
import pandas as pd
import os
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
from key_vars import download_filepath, earliest_report_year, final_report_year, pdf_links_fpath


# Scrape- Unicredit Bulbank

# Bank specific vars
bank = "fibank"
bank_url = "https://www.fibank.bg/bg/za-nas/finansovi-otcheti"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

print("Scraping Fibank reports")

# Go to unicredit homepage
driver.get(bank_url)
time.sleep(3)
# Screenshot homepage to track progress
driver.get_screenshot_as_file("screenshots/startPage.png")

# Pick up latest report year (first el of chosen class)
final_report_year_website = driver.find_element(By.XPATH, "/html/body/div/main/section[1]/div/div/ul[1]/ul/li/a").get_attribute("innerHTML")
final_report_year_website = re.findall(r'\d+', final_report_year_website)
final_report_year_website = int(final_report_year_website[0])

if final_report_year > final_report_year_website:
    final_report_year = final_report_year_website
    print(f"NOTE! Final report year requested is not available on the bank's website, using latest available- {final_report_year}")

# Define empty lists to fill with pdf information
pdf_file_links = []
pdf_file_names = []
count = 0

# Note already downloaded files to avoid duplicates
downloaded_files = os.listdir(download_filepath)

# Iterate from 1 to n years to parse as no benefit of using years, esp with poor structuring of reports list on website
n_years_to_parse = final_report_year-earliest_report_year+1

# Set years that have a half-year report
# NOTE-hard-coding which to avoid unnecessary complexity and checking on each iter as the website structure gives no indication either
years_two_reports = range(2009, 2014) #2013 last year with 2 reports
# Extra counter to accommodate for years with 2 reports
counter_add = 0

# Download all pdf reports for each year in specified range
for scraping_iter_i in range(0, n_years_to_parse):
    # Print out year being processed (going in reverse chronological order)
    reporting_year_i = final_report_year - scraping_iter_i
    print(f"Parsing Year ---> {reporting_year_i}")

    # Factor in whether a year has had 2 reports
    scraping_iter_i = scraping_iter_i + counter_add

    # Set n reports according to n_reports for given year
    if reporting_year_i in years_two_reports:
        n_reports = 2
    else:
        n_reports = 1
    
    print(f"TESTTTT -------->>>>>> {n_reports}")
    print(f"TESTTTT -------->>>>>> {scraping_iter_i}")

    # Get all reports for given year
    for i in range(1, n_reports+1):
        
        # Print out report number/index
        print(f"Parsing Report ---> {i}")

        # Determine list index for reporting year
        # Latest 3 years on its own, following ones are in a flat list
        if scraping_iter_i == 0:
            fin_report_xpath = "/html/body/div/main/section[1]/div/div/ul[1]/ul/li/a"
            fin_report_xpath_pdf = "/html/body/div/main/section[1]/div/div/ul[1]/ul/li/span[2]/a"
        elif scraping_iter_i == 1:
            fin_report_xpath = "/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/li/a"
            fin_report_xpath_pdf = "/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/li/span[2]/a"
        elif scraping_iter_i == 2:
            fin_report_xpath = "/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/ul/li/a"
            fin_report_xpath_pdf = "/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/ul/li/span[2]/a"
        else:
            list_index = scraping_iter_i - 2
            # Factor into index if doing second report
            if i > 1:
                list_index =  list_index + (i-1)
            
            fin_report_xpath = f"/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/ul/ul/li[{list_index}]/a"
            fin_report_xpath_pdf = f"/html/body/div/main/section[1]/div/div/ul[2]/ul/ul/ul/ul/li[{list_index}]/span[2]/a"

        # Factor into index if doing second report
        if i == 2:
            # Factor in for next year iter
            counter_add = counter_add + 1

        # Get pdf filename
        pdf_name = driver.find_element(By.XPATH, fin_report_xpath).get_attribute("innerHTML")
        # Log pdf name
        print(pdf_name)

        # Get report's pdf details
        pdf_url = driver.find_element(By.XPATH, fin_report_xpath_pdf).get_attribute("href")
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
bank_col_vals = [bank] * len(pdf_file_names)
pdf_downloads_info_old = pd.read_csv(pdf_links_fpath)
pdf_downloads_info_new = pd.DataFrame(list(zip(bank_col_vals, pdf_file_names, pdf_file_links)), columns = ["bank", "filename", "href"])
pdf_downloads_info = pd.concat([pdf_downloads_info_old, pdf_downloads_info_new], ignore_index=True)
pdf_downloads_info.to_csv(pdf_links_fpath, index = False)

# Quit driver
print(driver.current_url)
driver.quit()
