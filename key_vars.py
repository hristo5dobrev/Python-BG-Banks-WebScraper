import datetime


# Keywords to search for
keywords = ["artificial intelligence", " AI ", "big data", "cloud compute", "cloud computing",
             "blockchain", "fintech", "machine learning", "robotization", "innovation"
            "изкуствен интелект", " ИИ ", "големи данни", "облачно изчисление", "облачни изчисления",
            "изчисления в облак", "блокчейн", "финтех", "машинно обучение", "роботизация", "иновация", "иновации"]

# Set bounds for years to get reports for
earliest_report_year = 2008
final_report_year = datetime.datetime.now().year


# Key vars

# Supporting files paths
parsed_files_fpath = "supporting_files/parsed-files.csv"
pdf_links_fpath = "supporting_files/pdf_downloads_links.csv"

# Downloads path
download_filepath = "downloads/"
