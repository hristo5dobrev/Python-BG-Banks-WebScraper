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
bank = "dsk"
bank_url = "https://dskbank.bg/en/about-us/documents"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"

# Open chrome instance
driver = webdriver.Chrome(options=set_chrome_options())

print("Scraping DSK reports")

# Go to starting page
driver.get(bank_url)
driver.maximize_window()
time.sleep(3)
# Screenshot homepage to track progress
driver.get_screenshot_as_file("screenshots/startPage.png")

cookies_btn = driver.find_element(By.XPATH, "//*[@id='CybotCookiebotDialogBodyButtonAcceptAll']")
cookies_btn.click()

# Pick up latest report year (first el of chosen class)
final_report_year_website_fin_info = driver.find_element(By.XPATH, "/html/body/div[3]/main/div[2]/div/section[3]/div[1]/div[2]/div/div/select/option").get_attribute("innerHTML")
final_report_year_website_fin_info = int(final_report_year_website_fin_info)

if final_report_year > final_report_year_website_fin_info:
    print(f"NOTE! Final report year requested is not available on the bank's website for FINANCIAL INFO DOCS, using latest available- {final_report_year_website_fin_info}")


final_report_year_website_annnual_announcements = driver.find_element(By.XPATH, "/html/body/div[3]/main/div[2]/div/section[4]/div[1]/div[2]/div/div/select/option[1]").get_attribute("innerHTML")
final_report_year_website_annnual_announcements = int(final_report_year_website_annnual_announcements)

if final_report_year > final_report_year_website_annnual_announcements:
    print(f"NOTE! Final report year requested is not available on the bank's website for ANNUAL ANNOUNCEMENTS, using latest available- {final_report_year_website_annnual_announcements}")



# Define empty lists to fill with pdf information
pdf_file_links = []
pdf_file_names = []

# Note already downloaded files to avoid duplicates
downloaded_files = os.listdir(download_filepath)


# Download all pdf reports for each year in specified range


# Locate lists of all docs (across all years available on website)

years_fin_info = range(earliest_report_year, final_report_year_website_fin_info+1)
fin_info_webels = [driver.find_elements(By.XPATH, f"//*[contains(@class, 'files-list') and contains(@class, 'docLib') and contains(@class, '{year}')]") for year in years_fin_info]
n_fin_info_reports = len(fin_info_webels)

years_annual_announcements = range(earliest_report_year, final_report_year_website_annnual_announcements+1)
annual_announcements_webels = [driver.find_elements(By.XPATH, f"//*[contains(@class, 'files-list') and contains(@class, 'docLib2') and contains(@class, '{year}')]") for year in years_fin_info]
n_annual_announcement_reports = len(annual_announcements_webels)

annual_reports_separate = driver.find_elements(By.XPATH, "/html/body/div[3]/main/div[2]/div/section[5]/div/ul/li")


# Loop through all the financial info reports
for i in range(0, n_fin_info_reports):
    
    # Print out report number/index
    print(f"Parsing Report Year ---> {i}")

    current_year_webels = fin_info_webels[i][0]
    current_year_webels = current_year_webels.find_elements(By.TAG_NAME, "li")

    for j in range(0, len(current_year_webels)):
        
        # Avoid non-pdf files
        file_type = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__type").get_attribute("innerHTML")
        if "pdf" not in file_type.lower():
            continue

        # Take name and href
        pdf_url = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__link").get_attribute("href") 
        pdf_name = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__link").get_attribute("innerHTML")

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


# Loop through all the annual announcements reports
for i in range(0, n_annual_announcement_reports):
    
    # Print out report number/index
    print(f"Parsing Report Year ---> {i}")

    if len(annual_announcements_webels[i]) == 0:
        year_not_available = earliest_report_year+i
        print(f"NOTE! Report year requested is not available on the bank's website for ANNUAL ANNOUNCEMENTS- {year_not_available}")
        continue

    current_year_webels = annual_announcements_webels[i][0]
    current_year_webels = current_year_webels.find_elements(By.TAG_NAME, "li")

    for j in range(0, len(current_year_webels)):

        # Avoid non-pdf files
        file_type = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__type").get_attribute("innerHTML")
        if "pdf" not in file_type.lower():
            continue

        # Take name and href
        pdf_url = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__link").get_attribute("href") 
        pdf_name = current_year_webels[j].find_element(By.CLASS_NAME, "files-list__link").get_attribute("innerHTML")

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


# Loop through separated annual reports
for i in range(0, len(annual_reports_separate)):

    # Take name and href
    pdf_url = annual_reports_separate[i].find_element(By.CLASS_NAME, "files-list__link").get_attribute("href") 
    pdf_name = annual_reports_separate[i].find_element(By.CLASS_NAME, "files-list__link").get_attribute("innerHTML")

    # Check that doc is for year of interest
    doc_year = re.findall(r"\d+$", pdf_name)
    doc_year = int(doc_year[0])

    if doc_year not in range(earliest_report_year, final_report_year+1):
        continue

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
