import base64
import io
import json
import logging
import time

import pdfplumber
from selenium.webdriver.common.by import By

from app.crawler_util import find_valid_children_urls, get_loaded_fonts, get_css_referenced_fonts, \
    get_single_asset_size
from app.open_ai_client import extract_pdf_content

WAIT_SECONDS = 3
NETWORK_DATA_JS_PATH = "../js/network_data.js"
COMPUTED_FONTS_JS_PATH = "../js/computed_fonts.js"
logger = logging.getLogger("crawler")
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def extract_content(url, driver, config, pdf_config):
    logger.info("Extracting content from: " + url)
    all_rows = []

    try:
        driver.get(url)

        time.sleep(5)

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        page_title = driver.title

        logger.info("Extracting content from: " + page_title)

        for selector_config in config:
            css_selector = selector_config["css"]
            selector_type = selector_config.get("type", "text")
            attributes = selector_config.get("attributes", [])

            if selector_type == "table":
                logger.info("Extracting table from: " + page_title)
                # grab table element
                tables = driver.find_elements(By.CSS_SELECTOR, css_selector)

                for table in tables:
                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    logger.info("Found " + str(len(rows)) + " rows")
                    for row in rows:
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        logger.info("Extracting content from " + str(len(cells)) + " cells")
                        if not cells:
                            continue

                        if "columns" in selector_config:
                            # map columns dynamically
                            row_dict = {
                                col_name: cells[i].text.strip() if i < len(cells) else ""
                                for i, col_name in enumerate(selector_config["columns"])
                            }
                        else:
                            # fallback: just index cells
                            row_dict = {f"col_{i}": cell.text.strip() for i, cell in enumerate(cells)}

                        # optional: also extract links from cells
                        row_links = [
                            a.get_attribute("href")
                            for cell in cells
                            for a in cell.find_elements(By.TAG_NAME, "a")
                        ]

                        # Store links as semicolon-separated string
                        row_dict["_links"] = ";".join(row_links)

                        # If any links are PDFs, process them
                        pdf_results = []
                        for link in row_links:
                            if link and link.lower().endswith(".pdf"):
                                try:
                                    pdf_content = extract_pdf_content(link, pdf_config)
                                    pdf_results.append(pdf_content)
                                except Exception as e:
                                    logger.error(f"Failed to process PDF {link}: {e}")

                        if pdf_results:
                            row_dict["pdf_extracted"] = pdf_results
                        # Add page-level info
                        row_dict["url"] = url
                        row_dict["page_title"] = page_title

                        all_rows.append(row_dict)

                logger.info("Extracted " + str(len(all_rows)) + " rows from: " + page_title)
            else:
                logger.info("Extracting elements from: " + page_title)
                elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
                for element in elements:
                    element_dict = {
                        "text": element.text.strip(),
                        "url": url,
                        "page_title": page_title
                    }
                    # Extract attributes if configured
                    for attribute in attributes:
                        element_dict[attribute] = element.get_attribute(attribute)
                    all_rows.append(element_dict)

                logger.info("Extracted " + str(len(all_rows)) + " elements from: " + page_title)

            return all_rows

    except Exception as e:
        logger.error("Error extracting content from: " + url)
        logger.error(e)


def extract_assets(driver, page_title, network_script):
    try:
        logger.info("Extracting assets from: " + page_title)
        assets = []
        json_data = driver.execute_script(network_script)
        for entry in json.loads(json_data):
            asset_size = entry["Size"] or get_single_asset_size(entry["URL"])
            assets.append({
                "asset_url": entry["URL"],
                "asset_type": entry["Type"],
                "asset_size_byte": asset_size
            })
        logger.info("Extracted " + str(len(assets)) + " assets from: " + page_title)
        return assets

    except Exception as e:
        logger.error("Error extracting assets from: " + page_title)
        logger.error(e)


def extract_fonts(driver, page_title, network_script, font_script):
    try:
        logger.info("Extracting fonts from: " + page_title)
        json_data = driver.execute_script(network_script)
        font_data = json.loads(json_data)

        loaded_fonts = get_loaded_fonts(font_data)
        css_referenced_fonts = get_css_referenced_fonts(driver)
        computed_fonts = driver.execute_script(font_script)

        fonts = {
            "loaded_fonts": loaded_fonts,
            "css_referenced_fonts": css_referenced_fonts,
            "computed_fonts": computed_fonts
        }

        logger.info("Extracted loaded, css-referenced and computed fonts from: " + page_title)

        return fonts

    except Exception as e:
        logger.error("Error extracting fonts from: " + page_title)
        logger.error(e)


def extract_paragraphs_after_headings(pdf_file, rules):
    results = {}

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for rule in rules:
                heading = rule["heading"].lower()
                capture = rule.get("capture", "paragraph")

                for i, line in enumerate(lines):
                    if heading in line.lower():
                        # collect lines until blank or next heading
                        paragraph = []
                        for next_line in lines[i+1:]:
                            if not next_line.strip():
                                break
                            # stop if next heading appears
                            if any(r["heading"].lower() in next_line.lower() for r in rules):
                                break
                            paragraph.append(next_line)

                        if capture == "paragraph":
                            results[heading] = " ".join(paragraph).strip()
                        elif capture == "sentence":
                            sentence = paragraph[0].split(".")[0] + "."
                            results[heading] = sentence.strip()
                        elif capture == "page":
                            results[heading] = " ".join(lines[i+1:]).strip()

    return results


def process_pdf(driver, pdf_url, config):
    if config.get("enabled", False):
        logger.info("Processing pdf: " + pdf_url)
        rules = config.get("extract_rules", [])

        # Navigate directly to the PDF
        driver.get(pdf_url)

        # Use DevTools to get the raw PDF data
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {"format": "A4"})
        pdf_bytes = base64.b64decode(pdf_data["data"])

        # Extract text with pdfplumber
        with io.BytesIO(pdf_bytes) as pdf_file:
            results = extract_paragraphs_after_headings(pdf_file, rules)

        return {
            "pdf_url": pdf_url,
            "extracted": results
        }
    else:
        return {}


def crawl_iterative(driver, urls, is_extract_assets, is_extract_fonts, css_config, pdf_config):
    logger.info("Starting to crawl " + str(len(urls)) + " urls iteratively")
    elements_list = []

    if is_extract_assets or is_extract_fonts:
        with open(NETWORK_DATA_JS_PATH, "r") as js_file:
            network_script = js_file.read()

    if is_extract_fonts:
        with open(COMPUTED_FONTS_JS_PATH, "r") as js_file:
            font_script = js_file.read()

    for url in urls:
        all_rows = extract_content(url, driver, css_config, pdf_config)

        if is_extract_assets:
            assets = extract_assets(driver, url, network_script)
            elements_dict = {"assets": assets}
            all_rows.append(elements_dict)

        if is_extract_fonts:
            fonts = extract_fonts(driver, network_script, font_script)
            elements_dict = {"fonts": fonts}
            all_rows.append(elements_dict)

        elements_list.extend(all_rows)

    logger.info("Finished crawling " + str(len(urls)) + " urls iteratively gracefully")

    return elements_list


def crawl_recursive(driver, start_url, is_extract_assets, is_extract_fonts, css_config, pdf_config, blacklist_keywords, whitelist_keywords, termination_index):
    logger.info("Starting to crawl " + start_url + " recursively")

    elements_list = []
    urls_to_crawl = []
    index = 0

    if is_extract_assets or is_extract_fonts:
        with open(NETWORK_DATA_JS_PATH, "r") as js_file:
            network_script = js_file.read()

    if is_extract_fonts:
        with open(COMPUTED_FONTS_JS_PATH, "r") as js_file:
            font_script = js_file.read()

    def recursive_crawl(url, elements_list, index):
        all_rows = extract_content(url, driver, css_config, pdf_config)

        if is_extract_assets:
            assets = extract_assets(driver, url, network_script)
            elements_dict = {"assets": assets}
            all_rows.append(elements_dict)

        if is_extract_fonts:
            fonts = extract_fonts(driver, network_script, font_script)
            elements_dict = {"fonts": fonts}
            all_rows.append(elements_dict)

        new_urls_to_crawl = find_valid_children_urls(driver, urls_to_crawl, blacklist_keywords, whitelist_keywords)
        urls_to_crawl.extend(new_urls_to_crawl)

        elements_list.extend(all_rows)

        if index < termination_index:
            index += 1
            next_url = urls_to_crawl.pop(0)
            recursive_crawl(next_url, elements_list, index)

    recursive_crawl(start_url, elements_list, index)

    logger.info("Finished crawling " + str(len(urls_to_crawl)) + " urls recursively gracefully")

    return elements_list
