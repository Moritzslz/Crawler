#Web Crawler Project
## Introduction
This project allows you to extract and analyze data from websites. It supports multiple crawling methods and can extract information both from HTML pages and linked PDF documents. Project Structure

## Configuration File (config.json)
The crawler behavior is fully configurable via JSON. Key parameters include:
- logging_level: "INFO" (controls verbosity of logs).
- user_agent: Custom user agent string ("m" in this configuration).
- headless: false (GUI mode; set true for headless).
- disable_cache: true to prevent caching of pages.
- crawl_method: "i" for iterative, "r" for recursive.
- analyse_assets: false (disable asset analysis).
- analyse_fonts: false (disable font analysis).
- output_file_name: "output" (file name for the extracted data).
- output_sheet_name: "crawl_data" (sheet name if saving to Excel).
- iterative.input_file_name: "urls.csv" (list of URLs for iterative crawling).
- iterative.input_file_type: "csv" (type of input file).
- recursive.start_url: "https://www.cda-amc.ca/find-reports" (starting URL for recursive crawling).
- recursive.termination_index: 10 (max pages to crawl recursively).
- recursive.blacklist_keywords: Pages containing these keywords will be skipped.
- recursive.whitelist_keywords: Only URLs containing these keywords will be crawled.
- selectors: CSS selectors to extract tables, text, and links.
- pdf.enabled: true (enable PDF parsing).
- pdf.extract_rules: Sections of PDFs to extract, e.g., the eligibility and reimbursement sections.

## PDF Extraction Rules
The crawler will locate PDFs linked from pages and extract specific sections based on headings:
```json
"pdf": {
  "enabled": true,
  "extract_rules": [
    {
      "heading": "Which Patients Are Eligible for Coverage?",
      "capture": "paragraph"
    },
    {
      "heading": "What Are the Conditions for Reimbursement?",
      "capture": "paragraph"
    }
  ]
}
```
##Usage
Place input files in the input/ directory (e.g., urls.csv).
Adjust settings in config/config.json as needed.
Run the crawler:
python main.py
Extracted data, including parsed PDF sections, will be saved in the output/ directory under the file name specified in output_file_name.
Crawl Methods
Iterative Crawling (crawl_method: "i"): Crawl URLs listed in the input CSV file.
Recursive Crawling (crawl_method: "r"): Crawl starting from a URL, following links recursively up to termination_index.
Font Analysis: Disabled in this configuration.
Asset Analysis: Disabled in this configuration.
Example Selectors
