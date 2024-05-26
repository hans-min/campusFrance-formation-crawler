from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def select_option_from_dropdown(dropdown_text, option_texts):
    # Wait for the page to fully load
    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
    try:
        # Click the dropdown button by its text
        dropdown_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{dropdown_text}')]")))
        dropdown_button.click()

        for option_text in option_texts:
            option = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f"//label[contains(text(), '{option_text}')]")))
            option.click()    
        time.sleep(1)  # Wait for the page to load dynamically; adjust as necessary
        print(f"Selected '{option_texts}' from the '{dropdown_text}' dropdown")
    except Exception as e:
        print(f"An error occurred: {e}")

def go_to_next_page(page_number):
    element = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, f"//a[contains(@ng-click, 'setCurrent') and contains(text(), '{page_number}')]")))
    element.click()

def fetch_program_ids(base_url, page_range: int):
    '''
    Go to all the paginations and fetch all programs ids
    return: all program ids
    '''
    found_ids = set()  # Store found URLs here
    # Example: Find all <tr> tags and extract href attributes
    for page in range(1, page_range+1):
        program_ids = driver.find_elements(By.TAG_NAME, 'tr')
        print(f'Found {len(program_ids)} links on {base_url} on page {page}')
        for program_id in program_ids:
            id = program_id.get_attribute('id')
            if id and id.startswith('#ti'):
                href = id[3:] #remove #ti
                found_ids.add(href)
        if page < page_range: 
            go_to_next_page(page+1)
    return found_ids

def find_text_in_each_url(ids, words):
    urls_to_visit_manually = {}  # Store URLs to visit manually here
    while ids:
        current_id = ids.pop()
        current_url = base_url + '#/program/' + current_id
        driver.get(current_url)
        time.sleep(1)  # Wait for the page to load dynamically; adjust as necessary
        page_source = driver.page_source
        words_found = find_words_in_url(page_source, words)
        if words_found:
            urls_to_visit_manually[current_url] = words_found
    return urls_to_visit_manually

def find_words_in_url(page_source, words):
    # Get the page source and convert to lower case for case-insensitive search
    lower_page_source = page_source.lower()
    result = [word for word in words if word.lower() in lower_page_source]
    return result

def crawl_all_pages(url, words, page_range=26):
    driver.get(base_url)
    select_option_from_dropdown("Fields", ["Engineering and Technology"])
    select_option_from_dropdown("Level of degree", ["Master 2"])
    found_ids = fetch_program_ids(base_url, page_range)
    print(f'Found {len(found_ids)} URLs to crawl')
    urls_to_visit_manually = find_text_in_each_url(found_ids, words)
    
    print(f'Found {len(urls_to_visit_manually)} URLs to visit manually')
    for url in urls_to_visit_manually:
        print(f"URL: {url} contains the following words {urls_to_visit_manually[url]}")
    
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Initialize the WebDriver with the options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

base_url = 'https://taughtie.campusfrance.org/tiesearch/'
words = ["apprentissage", "alternance", "apprentice", " dual", "work-study", "online", "distance learning", "e-learning"]
crawl_all_pages(base_url, words, 17)

driver.quit()