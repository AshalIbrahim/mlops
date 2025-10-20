from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

page_start_num=1
page_end_num=10

cities=["Karachi-2","Lahore-1","Islamabad-3"]

categories=["Commercial","Homes","Plots","Rentals_Commercial","Rentals_Plots","Rentals"]


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def gen_url():
    urls = []
    for c in cities:
        for cat in categories:
            for p in range(1, 11):
                url = f"https://www.zameen.com/{cat}/{c}-{p}.html"
                urls.append(url)
    return urls


print(len(gen_url()))

def open_page():
    var = "Commercial"
    # Open a website
    driver.get("https://www.zameen.com/Homes/Karachi_D.H.A_Phase_5-1482-1.html?sort=date_desc")
    wait = WebDriverWait(driver, 10)
    extract_info()    # Keep browser open
    input("Press Enter to close...")
    driver.quit()

def extract_links():
    links=driver.find_elements(By.CSS_SELECTOR,'[aria-label="Listing link"]')
    written_links=[]
    driver.implicitly_wait(10)
    for l in links:
        driver.implicitly_wait(10)
        written_links.append(l.get_attribute('href'))
    
    return written_links
        # print(l.get_attribute('href'))

def parse_price(price_str: str) -> int:
    """
    Converts price strings like '8crore', '5lacs', '2.5lac' into numbers.
    Assumes Indian numbering system:
        1 crore = 10,000,000
        1 lakh/lac = 100,000
    """
    price_str = price_str.strip().lower()
    
    # Extract number part
    num = ""
    for ch in price_str:
        if ch.isdigit() or ch == ".":
            num += ch
        else:
            break
    
    # Default multiplier
    multiplier = 1
    
    if "crore" in price_str:
        multiplier = 10_000_000
    elif "lac" in price_str or "lakh" in price_str:
        multiplier = 100_000
    
    if num == "":
        raise ValueError(f"Could not extract numeric value from '{price_str}'")
    
    return int(float(num) * multiplier)


def extract_info():
    properties=[]
    links=extract_links()
    for l in links:
        driver.get(l)
        WebDriverWait(driver, 10)
        driver.execute_script("window.scrollBy(0, 500);")
        WebDriverWait(driver, 10)

        # detail_container=driver.find_element(By.CSS_SELECTOR,'[aria-label="Property details"]')
        # Extract fields
        prop_type = driver.find_element(By.CSS_SELECTOR, '[aria-label="Type"]').text
        covered_area = driver.find_element(By.CSS_SELECTOR, '[aria-label="Area"]').text
        price_elem = driver.find_element(By.CSS_SELECTOR, 'span[aria-label="Price"]')
        price_text = price_elem.get_attribute("textContent")
        location = driver.find_element(By.CSS_SELECTOR, '[aria-label="Location"]').text
        beds = driver.find_element(By.CSS_SELECTOR, '[aria-label="Beds"]').text
        baths = driver.find_element(By.CSS_SELECTOR, '[aria-label="Baths"]').text
        purpose = driver.find_element(By.CSS_SELECTOR, '[aria-label="Purpose"]').text

        amenities = [a.text for a in driver.find_elements(By.CLASS_NAME, "_3efd3392")]

        # Pack into tuple
        property_data = (
            prop_type,
            purpose,
            covered_area,
            price_text,
            location,
            beds,
            baths,
            amenities
        )
        properties.append(property_data)
    print(properties)
    header=[            "prop_type",
            "purpose",
            "covered_area",
            "price_text",
            "location",
            "beds",
            "baths",
            "amenities"]
    save_properties(properties,header)


def save_properties(data_tuples, header):
    """
    Saves all property tuples to 'properties.csv'.
    Overwrites the file each time it is called.
    """
    filename = "dha.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        for row in data_tuples:
            # Convert amenities list → comma-separated string
            row = [",".join(x) if isinstance(x, list) else x for x in row]
            writer.writerow(row)

    print(f"✅ File '{filename}' created/updated with {len(data_tuples)} records.")


        # print(property_data)

open_page()