# Supporting Functions

import os
from selenium.webdriver.chrome.options import Options



# Function to use for setting chrome options
def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    # CRASHES WITHOUT
    # Explicitly saying that this is a headless application- no browser GUI wanted
    # chrome_options.add_argument("--headless=new")
    # Explicitly bypassing the security level in Docker- as Docker daemon runs as root user Chrome chrashes
    # (https://stackoverflow.com/questions/50642308/webdriverexception-unknown-error-devtoolsactiveport-file-doesnt-exist-while-t)
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # NO CRASH WITHOUT- still necessary?- Yes!

    # Explicitly disabling the usage of /dev/shm/ . The /dev/shm partition is too small in certain VM environments, causing Chrome to fail or crash.
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify prefs
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs

    # Prefs vars
    # download_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
    download_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
    # download_dir = "C:\\devContainers-Python-ContractsParser/downloads"
    # download_dir = "C:\Users\HristoDobrev\Documents\Python\devContainers-Python-ContractsParser\downloads"
    #download_dir = f"{os.getcwd()}//downloads//"
    #content_settings = {"images": 2}
    
    # Disabling the images
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["download.default_directory"] = download_dir
    chrome_prefs["download.prompt_for_download"] = False
    chrome_prefs["download.directory_upgrade"] = True
    chrome_prefs["safebrowsing.enabled"] = True
    chrome_prefs["safebrowsing.disable_download_protection"] = False

    #print(json.dumps(my_dict, indent=4))
    
    # chrome_options.add_experimental_option("prefs", {
    #     "profile.default_content_settings": content_settings,
    #     "download.default_directory": download_dir,
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "safebrowsing.enabled": True
    # })


    # prefs = {
    #     "download.default_directory" : "/workspaces/devContainers-Python-ContractsParser/downloads",
    #     "download.directory_upgrade": True,
    #     "download.prompt_for_download": False
    #     }
    # chrome_options.add_experimental_option("prefs", prefs)
    
    #print(json.dumps(chrome_options.experimental_options, indent=4))

    return chrome_options