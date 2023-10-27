from app.crawler import *
from util.enums import *
from app.font_analyser import *

if __name__ == '__main__':

    # Setting base and fallback values
    input_file_path = "../input"
    output_file_path = "../output"
    user_agent = UserAgents.MOZILLA.value

    # Reading the config file
    with open("../config/config_thais.json", "r") as config_file:
        config = json.load(config_file)

    # Setting a user agent
    temp_user_agent = config["user_agent"]
    if temp_user_agent == "M":
        user_agent = UserAgents.MOZILLA.value
    if temp_user_agent == "S":
        user_agent = UserAgents.SAFARI.value
    if temp_user_agent == "O":
        user_agent = UserAgents.OPERA.value
    if temp_user_agent == "C":
        user_agent = UserAgents.CHROME.value
    if temp_user_agent == "F":
        user_agent = UserAgents.FIREFOX.value
    if temp_user_agent == "E":
        user_agent = UserAgents.EDGE.value
    if temp_user_agent == "A":
        user_agent = UserAgents.ANDROID_WEBKIT_BROWSER.value

    # setting the crawl method
    crawl_method = config["crawl_method"]
    # Using iterative crawl as a base fallback for wrong user input
    if 5 < crawl_method < 0:
        raise ValueError("A invalid number for the crawl method has been entered")

    # setting driver options
    headless = True
    disable_cache = True
    if config["headless"]:
        headless = True
    else:
        headless = False
    if config["disable_cache"]:
        disable_cache = True
    else:
        disable_cache = False

    # setting file names
    input_file_name = config["input_file_name"]
    input_file_type = config["input_file_type"]
    if 3 < input_file_type < 0:
        raise ValueError("A invalid number for the input file type method has been entered")
    output_file_name = config["output_file_name"]
    output_sheet_name = config["output_sheet_name"]

    # setting css selectors to extract
    css_selectors_to_extract = config["css_selectors_to_extract"]
    attribute_to_extract = config["attribute_to_extract"]

    # For crawling recursively
    start_url = config["start_url"]
    termination_index = config["termination_index"]
    forbidden_keywords = config["forbidden_keywords"]
    included_keywords = config["included_keywords"]

    if crawl_method == Crawl.RECURSIVE.value:
        crawl_recursive_css(headless, disable_cache, user_agent, start_url,
                            forbidden_keywords, included_keywords, termination_index, css_selectors_to_extract, attribute_to_extract)
        close_log("crawl_recursive_url_log")
        df = get_write_df()
        print(df)
        write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)

    if crawl_method == Crawl.ITERATIVE.value:
        url_df = read_file(input_file_type, input_file_path, input_file_name)
        urls = url_df["URL"]

        crawl_iterative_css(headless, disable_cache, user_agent, urls, css_selectors_to_extract, attribute_to_extract)
        df = get_write_df()
        print(df)
        write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)

    if crawl_method == Crawl.FONTS.value:
        url_df = read_file(input_file_type, input_file_path, input_file_name)
        urls = url_df["URL"]

        analyse_fonts(headless, disable_cache, user_agent, urls)
        df = get_write_df()
        print(df)
        write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)

    if crawl_method == Crawl.ASSETS_ITERATIVE.value:
        url_df = read_file(input_file_type, input_file_path, input_file_name)
        urls = url_df["URL"]

        get_assets_iterative(headless, disable_cache, user_agent, urls)
        df = get_write_df()
        print(df)
        write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)

    if crawl_method == Crawl.ASSETS_RECURSIVE.value:
        get_assets_recursive(headless, disable_cache, user_agent, start_url,
                             forbidden_keywords, included_keywords, termination_index)
        close_log("crawl_recursive_url_log")
        df = get_write_df()
        print(df)
        write_file(FileTypes.XLSX, output_file_path, output_file_name, output_sheet_name, df)

    if crawl_method == Crawl.TEST.value:
        print("Test")


