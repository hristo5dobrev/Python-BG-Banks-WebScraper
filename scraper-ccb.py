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
bank = "ccb"
bank_url = "https://www.ccbank.bg/bg/za-ckb/otcheti/godishni-otcheti"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

print("Scraping CCB reports")

# Go to starting page
driver.get(bank_url)
time.sleep(3)
# Screenshot homepage to track progress
driver.get_screenshot_as_file("screenshots/startPage.png")

# Pick up latest report year (first el of chosen class)
final_report_year_website = driver.find_element(By.XPATH, "//*[@id='block_201-zzzz']/div/div[2]/nav/nav[1]/a[1]").get_attribute("innerHTML")
final_report_year_website = int(final_report_year_website)

if final_report_year > final_report_year_website:
    final_report_year = final_report_year_website
    print(f"NOTE! Final report year requested is not available on the bank's website, using latest available- {final_report_year}")


# Define empty lists to fill with pdf information
pdf_file_links = []
pdf_file_names = []

# Note already downloaded files to avoid duplicates
downloaded_files = os.listdir(download_filepath)

# for reporting_year_i in range(earliest_report_year, final_report_year+1):
#     # Print out year being processed
#     print(f"Parsing Year ---> {reporting_year_i}")

#     # Show reports for given year
#     year_tab = driver.find_element(By.XPATH, f"//*[@id='block_201-zzzz']//*[@data-category-id='{reporting_year_i}-1' and @title='{reporting_year_i}']")


# Download all pdf reports for each year in specified range

# Locate list of all docs (across all years available on website)
reports_webels = driver.find_elements(By.XPATH, f"//*[@id='block_201-zzzz']/div/div[2]/ul/li")
n_reports = len(reports_webels)
# Loop through list of reports to stop when gone beyond earliest report year- list is in descending time order
stop_on_year = str(earliest_report_year-1)



# Loop through all the reports
# skip those of years outside range of interest
for i in range(0, n_reports):
    
    # Print out report number/index
    print(f"Parsing Report ---> {i}")

    # Check report year
    report_year_id = reports_webels[i].get_attribute("data-category-id")
    if stop_on_year in report_year_id:
        break

    # Take name and href
    pdf_url = reports_webels[i].find_element(By.CLASS_NAME, "file__link").get_attribute("href") 
    pdf_name = reports_webels[i].find_element(By.CLASS_NAME, "file__name").get_attribute("innerHTML")

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
