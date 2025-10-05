import re

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from util.enums import AssetTypes

PAGE_LOAD_TIMEOUT = 60

def init_driver_options(options, headless, disable_cache, user_agent):
    if headless:
        options.add_argument("--headless")
        options.add_argument("--user-agent=" + user_agent)
    if disable_cache:
        options.add_argument("--disable-cache")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-local-storage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
    options.add_argument("--incognito")
    options.add_argument("--enable-javascript")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return options


def init_chrome_diver(headless, disable_cache, user_agent):
    chrome_options = webdriver.ChromeOptions()
    chrome_options = init_driver_options(chrome_options, headless, disable_cache, user_agent)

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    return chrome_driver


def init_firefox_diver(headless, disable_cache, user_agent):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options = init_driver_options(firefox_options, headless, disable_cache, user_agent)
    firefox_options.add_argument("--devtools")

    firefox_driver = webdriver.Firefox(options=firefox_options)
    firefox_driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    return firefox_driver


def find_valid_children_urls(driver, urls_to_crawl, blacklist_keywords, whitelist_keywords):
    new_urls_to_crawl = []
    all_a_tags = driver.find_elements(By.TAG_NAME, "a")
    for a_tag in all_a_tags:
        href = a_tag.get_attribute("href")
        if href:
            # apply filters
            if blacklist_keywords and any(keyword.lower() in href.lower() for keyword in blacklist_keywords):
                continue
            if whitelist_keywords and not any(keyword.lower() in href.lower() for keyword in whitelist_keywords):
                continue
            if href not in urls_to_crawl and href not in new_urls_to_crawl:
                new_urls_to_crawl.append(href)

    return new_urls_to_crawl


def get_loaded_fonts(font_data):
    loaded_fonts_list = []
    font_name_pattern = re.compile("(\w+.\w+\.(?:woff2?|ttf))", re.IGNORECASE)

    for entry in font_data:
        if entry["Type"] == AssetTypes.LINK.value and ".woff" in entry["URL"] or ".ttf" in entry["URL"]:
            matches = font_name_pattern.search(str(entry))
            if matches:
                font_name = matches.group(1)  # Extract the font name from the first capture group
            else:
                font_name = "not_found"
            font_dict = {
                "loaded_font_name": font_name,
                "loaded_font_url": entry["URL"],
                "type": entry["Type"],
                "size": entry["Size"]
            }
            loaded_fonts_list.append(font_dict)

    return loaded_fonts_list


def get_css_referenced_fonts(driver):
    referenced_fonts_list = []
    tag_names_to_extract = ["p", "a", "h1", "h2", "h3"]

    def append_referenced_fonts_list(font_dict):
        if font_dict not in referenced_fonts_list:
            referenced_fonts_list.append(font_dict)

    body = driver.find_element(By.TAG_NAME, "body")
    body_fonts = body.value_of_css_property("font-family").split(", ")
    for font in body_fonts:
        font_dict = {
            "font_name": font
        }
        append_referenced_fonts_list(font_dict)

    for element_selector in tag_names_to_extract:
        elements = driver.find_elements(By.TAG_NAME, element_selector)
        for element in elements:
            element_fonts = element.value_of_css_property("font-family").split(", ")
            for font in element_fonts:
                font_dict = {
                    "font_name": font
                }
                append_referenced_fonts_list(font_dict)

    return referenced_fonts_list


def get_single_asset_size(asset_url):
    response = requests.get(asset_url)
    return len(response.content)  # Size of the response content in bytes
