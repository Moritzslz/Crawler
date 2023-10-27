import json
import time

import requests
from selenium.common import TimeoutException

from util.filehandler import append_write_df
from util.logger import *
from selenium import webdriver
from selenium.webdriver.common.by import By


# https://peter.sh/experiments/chromium-command-line-switches/

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

    return options


def init_chrome_diver(headless, disable_cache, user_agent):
    chrome_options = webdriver.ChromeOptions()
    chrome_options = init_driver_options(chrome_options, headless, disable_cache, user_agent)

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.set_page_load_timeout(60)

    return chrome_driver


def init_firefox_diver(headless, disable_cache, user_agent):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options = init_driver_options(firefox_options, headless, disable_cache, user_agent)
    firefox_options.add_argument("--devtools")

    firefox_driver = webdriver.Firefox(options=firefox_options)
    firefox_driver.set_page_load_timeout(60)

    return firefox_driver


def get_all_children_urls(urls_to_crawl, chrome_driver, forbidden_keywords, included_keywords):
    new_urls_to_crawl = []
    all_a_tags = chrome_driver.find_elements(By.TAG_NAME, "a")
    for a_tag in all_a_tags:
        href = a_tag.get_attribute('href')
        if href:
            if forbidden_keywords:
                if not any(keyword in href.lower() for keyword in forbidden_keywords):
                    if included_keywords:
                        if any(keyword in href.lower() for keyword in included_keywords):
                            if href not in urls_to_crawl:
                                new_urls_to_crawl.append(href)
                    else:
                        if href not in urls_to_crawl:
                            new_urls_to_crawl.append(href)
            else:
                if included_keywords:
                    if any(keyword in href.lower() for keyword in included_keywords):
                        if href not in urls_to_crawl:
                            new_urls_to_crawl.append(href)
                else:
                    if href not in urls_to_crawl:
                        new_urls_to_crawl.append(href)

    return new_urls_to_crawl


def crawl_recursive_css(headless, disable_cache, user_agent, start_url, forbidden_keywords, included_keywords, termination_index,
                        css_selectors_to_extract, attribute_to_extract):
    chrome_driver = init_chrome_diver(headless, disable_cache, user_agent)
    urls_to_crawl = []
    index = 0

    def recursive_crawl(url):
        nonlocal index
        elements_list = []
        global elements_dict
        log_start(url)
        try:
            chrome_driver.get(url)
            scroll_down(chrome_driver)
            page_title = chrome_driver.title

            new_urls_to_crawl = get_all_children_urls(urls_to_crawl, chrome_driver, forbidden_keywords, included_keywords)
            urls_to_crawl.extend(new_urls_to_crawl)

            for element_selector in css_selectors_to_extract:
                elements_dict = {"URL": url, "Page title": page_title}
                elements = chrome_driver.find_elements(By.CSS_SELECTOR, element_selector)
                if attribute_to_extract.lower() == "text":
                    elements_text = [element.text for element in elements]
                    elements_dict[element_selector + " : Text"] = elements_text
                if attribute_to_extract.lower():
                    attributes = [element.get_attribute(attribute_to_extract) for element in elements]
                    elements_dict[element_selector + " : " + attribute_to_extract] = attributes
                elements_dict["# " + element_selector + " elements"] = len(elements)
                elements_list.append(elements_dict)

            log_url(url)
            append_write_df(elements_list)
            log_end(page_title)

        except TimeoutException as e:
            log_exception("TimeoutException", url)
            elements_list.append(elements_dict)
            append_write_df(elements_list)
        except Exception as e:
            log_exception("Exception", url)
            elements_list.append(elements_dict)
            append_write_df(elements_list)

        if index < termination_index:
            index += 1
            next_url = urls_to_crawl.pop(0)
            log_urls_to_crawl(urls_to_crawl)
            recursive_crawl(next_url)

    recursive_crawl(start_url)

    chrome_driver.quit()
    log_text("Finished gracefully")


def crawl_iterative_css(headless, disable_cache, user_agent, urls, css_selectors_to_extract, attribute_to_extract):
    chrome_driver = init_chrome_diver(headless, disable_cache, user_agent)

    for url in urls:
        elements_list = []
        global elements_dict
        log_start(url)
        try:
            chrome_driver.get(url)
            scroll_down(chrome_driver)
            page_title = chrome_driver.title

            for element_selector in css_selectors_to_extract:
                elements_dict = {"URL": url, "Page title": page_title}
                elements = chrome_driver.find_elements(By.CSS_SELECTOR, element_selector)
                elements_text = [element.text for element in elements]
                if attribute_to_extract:
                    attributes = [element.get_attribute(attribute_to_extract) for element in elements]
                    elements_dict[attribute_to_extract] = attributes
                elements_dict[element_selector] = elements_text
                elements_dict["# " + element_selector + " elements"] = len(elements)
                elements_list.append(elements_dict)

            log_url(url)
            append_write_df(elements_list)
            log_end(page_title)

        except TimeoutException as e:
            log_exception("TimeoutException", url)
            elements_list.append(elements_dict)
            append_write_df(elements_list)
        except Exception as e:
            log_exception("Exception", url)
            elements_list.append(elements_dict)
            append_write_df(elements_list)

    chrome_driver.quit()
    log_text("Finished gracefully")


def get_single_asset_size(asset_url):
    response = requests.get(asset_url)
    return len(response.content)  # Size of the response content in bytes


def scroll_down(chrome_driver):
    chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


def get_assets_iterative(headless, disable_cache, user_agent, urls):
    chrome_driver = init_chrome_diver(headless, disable_cache, user_agent)

    with open("../js/network_data.js", "r") as js_file:
        script = js_file.read()

    for url in urls:
        asset_list = []
        global asset_dict
        log_start(url)
        try:
            chrome_driver.get(url)
            scroll_down(chrome_driver)
            page_title = chrome_driver.title

            json_data = chrome_driver.execute_script(script)
            asset_data = json.loads(json_data)

            for entry in asset_data:
                asset_dict = {"URL": url, "Page title": page_title}  # Creating new asset dict
                asset_size = entry["Size"]
                if asset_size == 0:
                    asset_size = get_single_asset_size(entry["URL"])
                asset_dict["Asset url"] = entry["URL"]
                asset_dict["Asset type"] = entry["Type"]
                asset_dict["Asset size in Byte"] = asset_size
                asset_list.append(asset_dict)

            log_url(url)
            append_write_df(asset_list)
            log_end(page_title)

        except TimeoutException as e:
            log_exception("TimeoutException", url)
            asset_list.append(asset_dict)
            append_write_df(asset_list)
        except Exception as e:
            log_exception("Exception", url)
            asset_list.append(asset_dict)
            append_write_df(asset_list)

    chrome_driver.quit()
    log_text("Finished gracefully")


def get_assets_recursive(headless, disable_cache, user_agent, start_url, forbidden_keywords, included_keywords, termination_index):
    chrome_driver = init_chrome_diver(headless, disable_cache, user_agent)
    urls_to_crawl = []
    index = 0

    with open("../js/network_data.js", "r") as js_file:
        script = js_file.read()

    def recursive_crawl(url):
        nonlocal index
        asset_list = []
        global asset_dict
        log_start(url)
        try:
            chrome_driver.get(url)
            scroll_down(chrome_driver)
            page_title = chrome_driver.title

            new_urls_to_crawl = get_all_children_urls(urls_to_crawl, chrome_driver, forbidden_keywords, included_keywords)
            urls_to_crawl.extend(new_urls_to_crawl)

            json_data = chrome_driver.execute_script(script)
            asset_data = json.loads(json_data)

            for entry in asset_data:
                asset_dict = {"URL": url, "Page title": page_title}  # Creating new asset dict
                asset_size = entry["Size"]
                if asset_size == 0:
                    asset_size = get_single_asset_size(entry["URL"])
                asset_dict["Asset url"] = entry["URL"]
                asset_dict["Asset type"] = entry["Type"]
                asset_dict["Asset size in Byte"] = asset_size
                asset_list.append(asset_dict)

            log_url(url)
            append_write_df(asset_list)
            log_end(page_title)

        except TimeoutException as e:
            log_exception("TimeoutException", url)
            asset_list.append(asset_dict)
            append_write_df(asset_list)
        except Exception as e:
            log_exception("Exception", url)
            asset_list.append(asset_dict)
            append_write_df(asset_list)

        if index < termination_index:
            index += 1
            next_url = urls_to_crawl.pop(0)
            log_urls_to_crawl(urls_to_crawl)
            recursive_crawl(next_url)

    recursive_crawl(start_url)

    chrome_driver.quit()
    log_text("Finished gracefully")
