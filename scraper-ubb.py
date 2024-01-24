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
bank = "ubb"
bank_url = "https://www.ubb.bg/en/about/reports"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
articles_output_fpath = f"outputs/search_results_articles_{bank}.csv"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

print("Scraping UBB reports")

# Go to unicredit homepage
driver.get(bank_url)
time.sleep(3)
# Screenshot homepage to track progress
driver.get_screenshot_as_file("screenshots/startPage.png")

# Decline cookies
cookies_btn = driver.find_element(By.XPATH, "//*[@id='CybotCookiebotDialogBodyButtonDecline']")
cookies_btn.click()
time.sleep(1)

# Pick up latest report year (first el of chosen class)
final_report_year_website = driver.find_element(By.CLASS_NAME, "archive-year").get_attribute("innerHTML")
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
for reporting_year_i in range(earliest_report_year, final_report_year+1):
    # Print out year being processed
    print(f"Parsing Year ---> {reporting_year_i}")

    # Determine div list index for reporting year
    div_n_for_reporting_year = (final_report_year - earliest_report_year + 1) - (reporting_year_i - earliest_report_year)

    # Use find_elements to see if there are any for given XPATH- specifically wrt given year
    check_reports_exist = driver.find_elements(By.XPATH, f"/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div[1]/div[{div_n_for_reporting_year}]/div[2]/a")
    n_reports = len(check_reports_exist)

    if len(check_reports_exist) == 0:
        continue

    # Get all reports for given year
    for i in range(1, n_reports+1):
        
        # Print out report number/index
        print(f"Parsing Report ---> {i}")

        # Find pdf report element and get filename
        xpath_fin_report_pdf_element = f"/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div[1]/div[{div_n_for_reporting_year}]/div[2]/a[{i}]"
        xpath_pdf_name = xpath_fin_report_pdf_element + "/div/h2"
        fin_report_pdf_element = driver.find_element(By.XPATH, xpath_fin_report_pdf_element)
        pdf_name = fin_report_pdf_element.find_element(By.XPATH, xpath_pdf_name).get_attribute("innerHTML")

        # Log pdf name
        print(pdf_name)

        # Get report's pdf details
        pdf_url = fin_report_pdf_element.get_attribute("href")
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
