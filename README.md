**Introduction**

This is a web crawling project that allows you to extract and analyze data from websites. It provides several methods for crawling websites and extracting information based on your configuration. This readme provides an overview of the project, its components, and how to use it.

**Project Structure**

The project is organized into several files and directories:

- crawler.py: Contains functions for web crawling and data extraction.
- font_analyser.py: Contains functions for analyzing web fonts.
- enums.py: Defines enumerations used in the project.
- filehandler.py: Provides functions for reading and writing data to files.
- logger.py: Defines logging functions to record the progress and any errors during crawling.
- network_data.js: JavaScript script for extracting network data from web pages.
- computed_fonts.js: JavaScript script for extracting computed fonts from web pages.
- input: This directory is intended for storing input files that you want to crawl.
- output: This directory is where the extracted data will be saved.
- config: Contains a configuration JSON file, as described below.
- logs: This directory is used to store log files generated during the crawling process.

**Configuration File**

The configuration for the web crawling process is stored in a JSON file named config.json. You can customize the following parameters in this file:

- user_agent: Set the user agent string for the web requests (e.g., "M" for Mozilla).
- crawl_method: Choose the method of crawling (1 for recursive, 2 for iterative, 3 for fonts, 4 for assets).
- headless: Set to true for headless mode (no GUI), false for GUI mode.
- disable_cache: Set to true to disable browser caching. (Recommended)
- input_file_name: Specify the name of the input file in the input directory.
- input_file_type: Define the input file type (1 for CSV, 2 for XLSX, 3 for JSON).
- output_file_name: Set the name of the output file in the output directory.
- output_sheet_name: Set the sheet name for the output file.
- css_selectors_to_extract: Define CSS selectors to extract data from web pages.
- start_url: Set the starting URL for recursive crawling.
- termination_index: Specify the maximum number of pages to crawl recursively. (Advised maximum: 1000)
- forbidden_keywords: Define a list of keywords that, when detected in a URL during recursive crawling, will result in excluding that URL from the crawl. (only for recursive crawling)
- included_keywords: Define a list of keywords that must be present in a discovered URL to initiate the crawling process during recursive crawling. (only for recursive crawling)

**Usage**

To use this web crawler, follow these steps:

- Place the input file to be crawled in the input directory.
- Configure the config.json file with your desired settings.
- Run the main.py script, and it will perform the web crawling and data extraction based on your configuration.
- The extracted data will be saved in the output directory.

**Crawl Methods**

- Recursive Crawling (Method 1): This method starts at a specified URL and recursively crawls linked pages, stopping when the termination index is reached or when no more links are available.
- Iterative Crawling (Method 2): This method iteratively crawls a list of URLs provided in the input file. 
- Analyze Fonts (Method 3): This method analyzes web fonts used on the provided URLs and extracts information about the fonts.
- Extract Assets Iterative (Method 4): This method extracts web assets (e.g., images, scripts, styles) and provides information about their size.
- Extract Assets Recursive (Method 5): This method extracts web assets (e.g., images, scripts, styles) and provides information about their size.

**Sample Configuration**

Here is an example of a configuration in config.json:
{
  "user_agent": "M",
  "crawl_method" : 1,
  "headless": false,
  "disable_cache": true,
  "input_file_name": "example_input.csv",
  "input_file_type": 1,
  "output_file_name": "example_output",
  "output_sheet_name": "output_data",
  "css_selectors_to_extract": ["h1", "p", "a"],
  "start_url": "example.com",
  "termination_index": 500,
  "forbidden_keywords": ["facebook", "youtube", "example-keyword"],
  "included_keywords": ["some.sub.domain.com"]
}

**Additional Notes**

Make sure to have the necessary Python dependencies installed.
You may need to customize the file paths or modify the code to suit your specific needs.

**Author**

This project is maintained by Moritz Schultz. If you have any questions or encounter issues, feel free to contact.

Enjoy web crawling with this project!
