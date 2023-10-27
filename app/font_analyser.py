import json
import re

from selenium.common import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from app.crawler import init_firefox_diver
from util.logger import *
from util.enums import AssetTypes
from util.filehandler import *


def get_loaded_fonts(font_data):
    loaded_fonts_list = []
    font_name_pattern = re.compile("(\w+.\w+\.(?:woff2?|ttf))", re.IGNORECASE)

    for entry in font_data:
        if entry["Type"] == AssetTypes.LINK.value and ".woff" in entry["URL"] or ".ttf" in entry["URL"]:
            matches = font_name_pattern.search(str(entry))
            if matches:
                font_name = matches.group(1)  # Extract the font name from the first capture group
            else:
                font_name = "Not Found"
            font_dict = {
                "Loaded font name": font_name,
                "Loaded font url": entry["URL"],
                "Loaded type": entry["Type"],
                "Loaded size": entry["Size"]
            }
            loaded_fonts_list.append(font_dict)

    return loaded_fonts_list


def get_css_referenced_fonts(chrome_driver, url):
    referenced_fonts_list = []
    tag_names_to_extract = ["p", "a", "h1", "h2", "h3"]

    def append_referenced_fonts_list(font_dict):
        if font_dict not in referenced_fonts_list:
            referenced_fonts_list.append(font_dict)

    try:
        body = chrome_driver.find_element(By.TAG_NAME, "body")
        body_fonts = body.value_of_css_property("font-family").split(", ")
        for font in body_fonts:
            font_dict = {
                "Font name": font
            }
            append_referenced_fonts_list(font_dict)

        for element_selector in tag_names_to_extract:
            elements = chrome_driver.find_elements(By.TAG_NAME, element_selector)
            for element in elements:
                element_fonts = element.value_of_css_property("font-family").split(", ")
                for font in element_fonts:
                    font_dict = {
                        "Font name": font
                    }
                    append_referenced_fonts_list(font_dict)

    except StaleElementReferenceException:
        log_exception("StaleElementReferenceException", url)
    except Exception:
        log_exception("Exception", url)

    return referenced_fonts_list


def analyse_fonts(headless, disable_cache, user_agent, urls):
    firefox_driver = init_firefox_diver(headless, disable_cache, user_agent)

    with open("../js/network_data.js", "r") as js_file:
        network_script = js_file.read()

    with open("../js/computed_fonts.js", "r") as js_file:
        font_script = js_file.read()

        for url in urls:
            font_audit_list = []
            global audit_dict
            log_start(url)
            try:
                firefox_driver.get(url)
                page_title = firefox_driver.title

                json_data = firefox_driver.execute_script(network_script)
                font_data = json.loads(json_data)

                loaded_fonts = get_loaded_fonts(font_data)
                css_referenced_fonts = get_css_referenced_fonts(firefox_driver, url)
                computed_fonts = firefox_driver.execute_script(font_script)

                audit_dict = {"URL": url, "Page title": page_title, "loaded_fonts": loaded_fonts,
                              "css_referenced_fonts": css_referenced_fonts, "computed fonts": computed_fonts}
                font_audit_list.append(audit_dict)

                log_url(url)
                append_write_df(font_audit_list)
                log_end(page_title)

            except TimeoutException:
                log_exception("TimeoutException", url)
                font_audit_list.append(audit_dict)
                append_write_df(font_audit_list)
            except Exception:
                log_exception("Exception", url)
                font_audit_list.append(audit_dict)
                append_write_df(font_audit_list)

            firefox_driver.quit()
            log_text("Finished gracefully")
