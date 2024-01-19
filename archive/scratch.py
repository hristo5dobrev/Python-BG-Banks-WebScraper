# Not used but useful snippets

#fin_report_pdf_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='2022-id']/div/div/ul/li/a")))

# # Getting attr values after using find_elementS
# # else can simply use get_attribute and attribute name for single el selected!
# for webel in language_btn_li:
#     # get element inner html
#     element_html = webel.get_attribute("innerHTML").strip()
#     print(BeautifulSoup(element_html, "html.parser").a.attrs["href"])


# # Click pdf (need to scroll to it)
# # LIVE ISSUE IN SELENIUM AND HEADLESS WHEN LONGER LOADING PDF IS THE NEW TAB
# # Define wait obj with timeout
# wait = WebDriverWait(driver, 10)
# original_window = driver.current_window_handle
#
# driver.execute_script("arguments[0].scrollIntoView();", fin_report_pdf_element)
# fin_report_pdf_element.click()
# time.sleep(5)
# # Go to pdf tab
# # Wait for the new window or tab- LIVE ISSUE IN SELENIUM AND HEADLESS WHEN LONGER LOADING PDF IS THE NEW TAB
# wait.until(EC.number_of_windows_to_be(2))
# window_handles = driver.window_handles
# driver.switch_to.window(window_handles[-1])
# # Loop through until we find a new window handle
# for window_handle in driver.window_handles:
#     if window_handle != original_window:
#         driver.switch_to.window(window_handle)
#         break
# # Close pdf tab and switch back
# driver.close()
# driver.switch_to.window(window_handles[0]) # original_window

# # Searching ON web page

# # Get full page html bs4.BeautifulSoup obj
# soup_page = BeautifulSoup(driver.page_source, "html.parser")
# source_page = driver.page_source

# # Searching in page source
# keywords = ["Начало Спестявания и инвестиции", "Документи за клиента"]
# print("Начало Спестявания и инвестиции" in source_page)
# found_keywords = [keyword for keyword in keywords if keyword in source_page]
# print(found_keywords)

# # Searching in soup
# print(soup_page(text=re.compile("Начало Спестявания и инвестиции")))
# print(soup_page(title="Документи за клиента"))

# soup = BeautifulSoup(pagination_bar.get_attribute('innerHTML'), 'html.parser')


# # Set up downloading loc and behaviour
# driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
# params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_filepath}}
# #params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': '/workspaces/devContainers-Python-ContractsParser/downloads'}}
# command_result = driver.execute("send_command", params)

ubb_url = "https://www.ubb.bg/"

#pattern = re.compile(r'\b{}\b'.format(re.escape(keyword)), re.IGNORECASE)
# pattern = r'\b{}\b'.format(re.escape(keyword))
#matches = re.finditer(pattern, page_text, re.IGNORECASE)

download_filepath = "downloads"
pdf_name = "TEST_unicr"
import requests
pdf_url = 'https://www.unicreditbulbank.bg/media/filer_public/e4/1e/e41e4296-117f-4907-b8a5-99742b07126e/unicredit-bulbank-unconsolidated-annual-disclosure-2008.pdf'
#pdf_url = "https://www.unicreditbulbank.bg/media/filer_public/25/70/25703b2e-6904-4e17-a46a-15ff51ce486a/unikredit_bulbank_godishen_otchet_2022.pdf"
#pdf_url = "https://www.africau.edu/images/default/sample.pdf"
#headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
headers = {'user-agent': 'testis'}
#r = requests.get(url, stream = True, headers = headers)
response = requests.get(pdf_url, stream=True, headers=headers)#, timeout=25)
print(response.status_code)
if response.status_code == 200:
    with open(f"{download_filepath}/{pdf_name}.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)