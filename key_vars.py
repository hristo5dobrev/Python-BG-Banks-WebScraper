import datetime


# Keywords to search for
keywords = ["artificial intelligence", " AI ", "big data", "cloud compute", "cloud computing", "blockchain",
            "изкуствен интелект", " ИИ ", "големи данни", "облачно изчисление", "облачни изчисления",
            "изчисления в облак", "блокчейн"]


# Choose bank via (un)commenting
# Unicredit vars - DONE
# bank = "unicredit"
# bank_url = "https://www.unicreditbulbank.bg/bg/individualni-klienti/"
# bank_news_url = "https://www.unicreditbulbank.bg/bg/za-nas/media/novini/"
# UBB (KBC) vars - WIP
bank = "ubb"
bank_url = "https://www.ubb.bg/en/about/reports"
bank_news_url = "https://www.ubb.bg/en/news"
# Fibank vars - NOT IMPLEMENTED
# bank = "fibank"
# bank_url = "https://www.fibank.bg/bg/za-nas/finansovi-otcheti"
# bank_news_url = "https://www.unicreditbulbank.bg/bg/za-nas/media/novini/"

# Set bounds for years to get reports for
earliest_report_year = 2008
final_report_year = datetime.datetime.now().year


# Key vars

# Unicredit specific- used to navigate to results webpage
desired_text_results_page = "Резултати"
# Supporting files paths
parsed_files_fpath = "supporting_files/parsed-files.csv"
pdf_links_fpath = "supporting_files/pdf_downloads_links.csv"
# Outputs fpaths
records_fname = f"outputs/recorded_matches_{bank}.csv"
articles_output_fpath = f"outputs/search_results_articles_{bank}.csv"

# Downloads path
download_filepath = "downloads/"
# Download reports in separate folder wrt bank
download_filepath = download_filepath + bank + "/"