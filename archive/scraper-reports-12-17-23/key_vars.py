import datetime

# Keywords to search for
keywords = ["artificial intelligence", " AI ", "big data", "cloud compute", "cloud computing", "blockchain",
            "изкуствен интелект", " ИИ ", "големи данни", "облачно изчисление", "облачни изчисления",
            "изчисления в облак", "блокчейн"]

# Key vars
unicredit_url = "https://www.unicreditbulbank.bg/bg/individualni-klienti/"
unicredit_news_url = "https://www.unicreditbulbank.bg/bg/za-nas/media/novini/"
download_filepath = "downloads"

# Fin reports extracting- key vars
download_filepath_reports = download_filepath + "/"
desired_text_results_page = "Резултати"
parsed_files_fpath = "parsed-files.csv"
# Set bounds for years to get reports for
earliest_report_year = 2008
final_report_year = datetime.datetime.now().year