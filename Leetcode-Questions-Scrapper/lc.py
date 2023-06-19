# Import required packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup


# Set up Selenium webdriver
# Define the webdriver service
s = Service("/usr/local/bin/chromedriver")   

# Intantiate the webdriver
driver = webdriver.Chrome(service = s)  # You may need to provide the path to your chromedriver executable

# # The base URL for the pages to scrape
PAGE_BASE_URL = "https://leetcode.com/problemset/all/?page="  # Replace with your desired URL

# Fucntion will get all the links (href) from "a" tag which are matching "/problem" pattern
def get_a_tags():
    # Get the page source
    page_source = driver.page_source
    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')
        # print(soup.title.get_text())
    
    # Get all "a" tags
    a_tags = soup.find_all("a")
    problem_links_unclean = []
    # Take only problem links -> Check for "/problem" pattern in 'href' of 'a' tags
    for link in a_tags:
        try:
            if "/problem" in link.get("href"):
                problem_links_unclean.append(link.get("href"))
        except:
            pass
    # Remove duplicates links using set
    problem_links_unclean = list(set(problem_links_unclean))
    
    # Return the list of unclean links
    return problem_links_unclean

# List to store the final list of Links
def get_all_links(url,total_pages):

    # Load the URL in the chrome browser
    driver.get(url)
    # Wait for some time (7 sec) so that page gets loaded
    time.sleep(7)

    # List to store the final list of links of all pages
    links = [] 
    # Loop throgh the "total_pages" and append the current page links into "links" list
    for i in range(1,total_pages+1):
        links += get_a_tags()
        '''
        # This method is I specially used for leetcode -> we used "search_element by xpath" + "click on it " to move to the next page 
        # Steps to do this :
            1. Right click on the next element button & Inspect
            2. While inspecting , in inspecting tab right click -> copy -> full Xpath
            3. Copy the xpath in a variable 
            4. Search element by xpath (using selenium) & click on it
        # I did so because Leetcode wasn't allowing to go to specific webpage by url. It automatically redirects/loads the first page.
        '''
        if i != total_pages: # Because last page will not have next button
            X_PATH = "/html/body/div[1]/div/div[2]/div[1]/div[1]/div[5]/div[3]/nav/button[10]"
            element = driver.find_element("xpath",X_PATH)
            element.click() 
            time.sleep(7)
    # Remove duplicates links using set
    links = list(set(links))  
    # Returns final links list    
    return links


total_pages = 55
links = []
links = get_all_links(PAGE_BASE_URL,total_pages)

# Open a file to write the results (links) to
with open('lc_links_unclean.txt', 'a') as f:
    # Iterate over each link in your final list
    for link in links:
        # Write each link to the file, followed by a newline
        f.write(link+'\n')

# Close the Selenium webdriver
driver.quit()