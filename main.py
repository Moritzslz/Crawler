import json
import logging

from app.crawler import crawl_recursive, crawl_iterative
from app.crawler_util import init_chrome_diver, init_firefox_diver
from util.enums import *
from util.filehandler import get_write_df, read_file, write_file, append_write_df


if __name__ == '__main__':
    input_file_path = "./input"
    output_file_path = "./output"

    # Reading config file
    with open("./config/config.json", "r") as config_file:
        config = json.load(config_file)

    # Read from config
    log_level_str = config.get("logging_level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger("main")

    logger.info("Config: " + str(config))

    # Setting output file names
    output_file_name = config["output_file_name"]
    output_sheet_name = config["output_sheet_name"]

    # Setting user agent
    user_agent = None
    config_user_agent = config["user_agent"]
    if config_user_agent.lower() == "m":
        user_agent = UserAgents.MOZILLA.value
    if config_user_agent.lower() == "s":
        user_agent = UserAgents.SAFARI.value
    if config_user_agent.lower() == "o":
        user_agent = UserAgents.OPERA.value
    if config_user_agent.lower() == "c":
        user_agent = UserAgents.CHROME.value
    if config_user_agent.lower() == "f":
        user_agent = UserAgents.FIREFOX.value
    if config_user_agent.lower() == "e":
        user_agent = UserAgents.EDGE.value
    if config_user_agent.lower() == "a":
        user_agent = UserAgents.ANDROID_WEBKIT_BROWSER.value
    if user_agent is None:
        raise ValueError("An invalid user agent has been configured")

    # Setting crawl method
    crawl_method = None
    config_crawl_method = config["crawl_method"]
    if config_crawl_method.lower() == "r":
        crawl_method = Crawl.RECURSIVE.value
    if config_crawl_method.lower() == "i":
        crawl_method = Crawl.ITERATIVE.value
    if crawl_method is None:
        raise ValueError("An invalid crawl method has been configured")

    logger.info("Crawl method: " + str(crawl_method))

    # Setting crawling options
    analyse_assets = False
    if config["analyse_assets"]:
        analyse_assets = True
    else:
        analyse_assets = False

    analyse_fonts = False
    if config["analyse_fonts"]:
        analyse_fonts = True
    else:
        analyse_fonts = False

    # Setting driver options
    headless = True
    if config["headless"]:
        headless = True
    else:
        headless = False

    disable_cache = True
    if config["disable_cache"]:
        disable_cache = True
    else:
        disable_cache = False

    # Setting iterative crawl options
    if crawl_method == Crawl.ITERATIVE.value:
        iterative_cfg = config["iterative"]
        input_file_name = iterative_cfg["input_file_name"]

        input_file_type = None
        config_input_file_type = iterative_cfg["input_file_type"]
        if config_input_file_type.lower() == "csv":
            input_file_type = FileTypes.CSV.value
        if config_input_file_type.lower() == "xlsx":
            input_file_type = FileTypes.XLSX.value
        if config_input_file_type.lower() == "json":
            input_file_type = FileTypes.JSON.value
        if input_file_type is None:
            raise ValueError("An invalid file format for the input file has been configured")

    # Setting recursive crawl options
    if crawl_method == Crawl.RECURSIVE.value:
        recursive_cfg = config["recursive"]
        start_url = recursive_cfg["start_url"]
        termination_index = recursive_cfg["termination_index"]
        blacklist_keywords = recursive_cfg["blacklist_keywords"]
        whitelist_keywords = recursive_cfg["whitelist_keywords"]

    # Setting css selectors to extract
    css_selector_config = config["selectors"]
    pdf_extraction_config = config["pdf"]

    driver = None
    if analyse_fonts:
        driver = init_firefox_diver(headless, disable_cache, user_agent)
    else:
        driver = init_chrome_diver(headless, disable_cache, user_agent)

    crawl_data = None
    if crawl_method == Crawl.RECURSIVE.value:
        crawl_data = crawl_recursive(driver, start_url, analyse_assets, analyse_fonts, css_selector_config, pdf_extraction_config, blacklist_keywords, whitelist_keywords, termination_index)

    if crawl_method == Crawl.ITERATIVE.value:
        url_df = read_file(input_file_type, input_file_path, input_file_name)
        urls = url_df["URL"]
        crawl_data = crawl_iterative(driver, urls, analyse_assets, analyse_fonts, css_selector_config, pdf_extraction_config)

    driver.quit()

    if crawl_data is None:
        raise Exception("Crawling failed")

    append_write_df(crawl_data)
    df = get_write_df()
    print(df)
    write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)


