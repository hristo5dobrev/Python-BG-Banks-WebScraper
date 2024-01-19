import os
import re
import PyPDF2
import datetime
import pandas as pd
from key_vars import download_filepath, parsed_files_fpath, keywords

# Script to parse downloaded pdf-s
# Searching for a set of key words within and returning associated information

# Check out files in location
files = os.listdir(download_filepath)
parsed_files = pd.read_csv(parsed_files_fpath)
files_links = pd.read_csv("pdf_downloads_links.csv")

# Exclude already parsed files
todo_files = [filename for filename in files if filename not in parsed_files["filename"].tolist()]

# Identify corresponding links to files to process
todo_files_links = []
for i in range(0, len(todo_files)):
    filename = todo_files[i]
    file_link = files_links[files_links["filename"]==filename].reset_index(drop = True).loc[0]["href"]
    todo_files_links.append(file_link)

# Empty lists to store match info
matching_pages = []
matching_paragraphs = []
matching_kwords = []
document_names = []
document_links = []

# Open files one by one and search for keywords
# store paragraphs where match found
for i in range(len(todo_files)):
    # Specify file path
    filepath = download_filepath + "/" + todo_files[i]
    # Log file being searched
    print(f"Doing file {todo_files[i]}----------------------------------")

    # Open the PDF file
    with open(filepath, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(filepath)

        # Loop through each page
        for page_n in range(len(pdf_reader.pages)):
            # Take page text
            page = pdf_reader.pages[page_n]
            page_text = page.extract_text()
            
            # Search for keywords using regular expressions with word boundaries
            for keyword in keywords:
                pattern = re.compile(keyword, re.IGNORECASE)
                
                # Get iterable mathces object
                matches = re.finditer(pattern, page_text)

                # Extract match specifics
                for match in matches:                    
                    # print(match)

                    # Note match page and text
                    # Add 1 to page_number to make it 1-based
                    matching_pages.append(page_n + 1)
                    matching_kwords.append(keyword)
                    document_names.append(todo_files[i])
                    document_links.append(todo_files_links[i])

                    # # Extract words_around number of words either side of match
                    # # NOTE- Approach Dropped
                    # words_around = 20
                    # start_pos = max(match.start() - words_around, 0)
                    # end_pos = min(match.end() + words_around, len(page_text))

                    # Find the start/end of the paragraph by searching for the nearest line break before/after the keyword
                    start_pos = page_text.rfind('\n', 0, match.start()) + 1 if match.start() > 0 else 0
                    end_pos = page_text.find('\n', match.end())

                    # Extract the string/paragraph containing the keyword
                    paragraph = page_text[start_pos:end_pos].strip()

                    # Add the paragraph to the list
                    matching_paragraphs.append(paragraph)


# Put together matches and pages
colnames = ["file", "href", "keyword", "match_page", "text"]
matches_new = pd.DataFrame(list(zip(document_names, document_links, matching_kwords, matching_pages, matching_paragraphs)),
                            columns = colnames)


# Add to recorded matches
records_fname = "recorded_matches.csv"
matches_previous = pd.read_csv(records_fname)
matches_full = pd.concat([matches_previous, matches_new], ignore_index=True)
matches_full.to_csv(records_fname, index=False)

# Add to parsed files to avoid re-doing
# NOTE implications if new files have same name as old!
# add rows to parsed_files which are todo_files (list) and sys.now
time_parsing_complete = [datetime.datetime.now()] * len(todo_files)
todo_files_df = pd.DataFrame(list(zip(todo_files, todo_files_links, time_parsing_complete)),
                             columns= ["filename", "href", "parsed"])
parsed_files = pd.concat([parsed_files, todo_files_df], ignore_index=True)
parsed_files.to_csv(parsed_files_fpath, index=False)
