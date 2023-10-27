import pandas as pd
import logging
from util.enums import FileTypes
from util.filehandler import write_file

log_df = pd.DataFrame(columns=["URL"])

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (e.g., INFO, DEBUG, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

event_logger = logging.getLogger("event_logger")
url_logger = logging.getLogger("url_logger")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

event_file_handler = logging.FileHandler('../logs/event.log')
event_file_handler.setLevel(logging.INFO)
event_file_handler.setFormatter(formatter)

url_file_handler = logging.FileHandler('../logs/crawled_url.log')
url_file_handler.setLevel(logging.INFO)
url_file_handler.setFormatter(formatter)

event_logger.addHandler(event_file_handler)
url_logger.addHandler(url_file_handler)


def log_start(url):
    event_logger.info("Starting crawl on " + url + " ...")


def log_end(page_title):
    event_logger.info("Successfully crawled " + page_title)


def log_text(text):
    event_logger.info(text)


def log_url(url):
    url_logger.info(url)


def log_exception(exception, url):
    url_logger.error(exception + " on " + url + " occurred")


def log_urls_to_crawl(urls_to_crawl):
    global log_df
    new_row = pd.DataFrame(urls_to_crawl)
    log_df = pd.concat([log_df, new_row], ignore_index=True)


def close_log(output_file_name):
    global log_df
    write_file(FileTypes.CSV, "../logs", output_file_name, None, log_df)
