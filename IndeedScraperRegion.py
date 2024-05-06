import csv
import time
from collections.abc import MutableMapping
import random
from random import randint
import time
from time import sleep
import os
import queue
import sys
import os
import asyncio
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os, certifi
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import random
import time
# Locate elements on page and throw error if they do not exist
from selenium.common.exceptions import NoSuchElementException
import re


def find_element_safe(driver, by, value):
    """ Attempt to find an element and return its text or None if not found. """
    try:
        element = driver.find_element(by, value)
        return element.text
    except NoSuchElementException:
        return None

def find_attribute_safe(driver, by, value, attribute):
    """ Attempt to find an element and return a specific attribute or None if not found. """
    try:
        element = driver.find_element(by, value)
        return element.get_attribute(attribute)
    except NoSuchElementException:
        return None


# Function to get a random user-agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)

def find_jobs(driver):
    try:
        job_count_text = driver.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount').text
#         max_iter_pgs = int(re.sub(r'\D', '', job_count_text.split(' ')[0])) // 15
        
        # Extract the number of jobs from the text
        job_count = int(re.search(r'\d+', job_count_text).group())

        # Calculate the number of pages based on the job count
        max_iter_pgs = (job_count // 15) + 1
        print(f"Total pages to iterate: {max_iter_pgs}")
        # Continue with your processing logic here
        return max_iter_pgs
    except NoSuchElementException:
        print("No jobs found against that criteria.")
        return

# Function to scrape job data
def scrape_indeed_jobs(region_url,keyword_name, job_location):
    try:
        initial_job_location = job_location
        # Initialize Chrome WebDriver using WebDriverManager
#         driver = webdriver.Chrome(ChromeDriverManager().install())

#         # Navigate to Indeed
#         driver.get(url)
        #       Find search fields and input keyword and location
        keyword_input = driver.find_element("name", "q")
        keyword_input.send_keys(keyword_name)

        location_input = driver.find_element("name", "l")
        location_input.clear()
        location_input.send_keys(job_location)

        location_input.send_keys(Keys.RETURN)

        # Wait for search results to load
        time.sleep(5)  # Adjust sleep time as needed
        
        max_iter_pgs = find_jobs(driver)
#         p=driver.find_element(By.CLASS_NAME,'jobsearch-JobCountAndSortPane-jobCount').text
#         max_iter_pgs = int(re.sub(r'\D', '', p.split(' ')[0]))//15  + 1

        print(max_iter_pgs)
        job_data = []
        for i in range(0,max_iter_pgs):
            print(keyword_name, job_location)
#             if i != 0:
            initial_keyword_name = '+'.join(keyword_name.split())
            initial_job_location = '+'.join(initial_job_location.split())
            scrape_page_url = '{}/jobs?q={}&l={}&start={}'.format(region_url,initial_keyword_name, job_location, i * 10)
#             scrape_page_url = 'https://www.indeed.com/jobs?q={}&l={}&start={}'.format(initial_keyword_name, initial_job_location,i * 10)
            print(scrape_page_url)
            driver.get(scrape_page_url)
            
            job_page = driver.find_element(By.ID,"mosaic-jobResults")
            jobs_li = job_page.find_elements(By.CLASS_NAME,"job_seen_beacon")
            
            for card in jobs_li:
                #Extracting job title
                title = card.find_element(By.CSS_SELECTOR, 'h2.jobTitle > a').get_attribute('innerText')
#                 print(title)
                # Extracting company name
                company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text
#                 print(company)
                # Extracting location
                location = card.find_element(By.CSS_SELECTOR, 'div[data-testid="text-location"]').text
#                 print(location)                    
                description = driver.find_elements(By.CSS_SELECTOR, "ul.css-9446fg li")  # This returns a list of elements
                description_text = '\n'.join([elem.text for elem in description])
#                 print(description_text)
                # companyLogoUrl is not provided in the HTML snippet
                application_url = card.find_element(By.CSS_SELECTOR, "h2.jobTitle > a").get_attribute('href')
#                 print(application_url)
                # userId is not provided in the HTML snippet
                # premium is not provided in the HTML snippet
    #             salary = card.find_element(By.CSS_SELECTOR, "div.salary-snippet-container").text
    #             print(salary)
                salary = ''
                try: # I removed the metadata attached to this class name to work!
                    salary = card.find_element(By.CLASS_NAME,"salary-snippet-container").text
                except NoSuchElementException: 
                    try: 
                        salary = card.find_element(By.CLASS_NAME,"estimated-salary").text

                    except NoSuchElementException:
                        salary = None
                
                scrape_job = {
#                         "slug": slug,
                        "title": title,
#                         "type": type,
#                         "locationType": locationType,
                        "location": location,
                        "description": description_text,
                        "companyName": company,
#                         "companyLogoUrl": companyLogoUrl,
                        "applicationUrl": application_url,
#                         "userId": userId,
#                         "premium": premium,
                        "salary": salary,
                    }
                print(scrape_job)
                job_data.append(scrape_job)
            print(i)
#             driver.get(f"https://www.indeed.com/jobs?q={keyword}&l={location}&start={i*15}")
#             sleep(randint(2, 4))    
        # Close the browser
#         driver.quit()

        return job_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# In[8]:


# Function to save data to JSON file
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Set the path to your Chrome WebDriver executable
webdriver_path = 'C:\\Users\\Dell\Downloads\\chromedriver-win64\\chromedriver.exe'
# Set the number of proxy rotations
num_proxy_rotations = 5

# Set the URL of the web page you want to scrape
login_page_url = 'https://inpol.mazowieckie.pl/login'

# Finding location, position, radius=35 miles, sort by date and starting page
paginaton_url = 'https://www.indeed.com/jobs?q={}&l={}&radius=35&filter=0&sort=date&start={}'
paginated_url = 'https://www.indeed.com/jobs?q={}&l={}$start={}' 


# In[4]:


headers = [
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36','Accept':'text/html'},
        {'User-Agent':'Windows 10/ Edge browser: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246','Accept':'text/html'}, 
        {'User-Agent': 'Windows 7/ Chrome browser:  Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36','Accept':'text/html'},
        {'User-Agent':'Mac OS X10/Safari browser: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9','Accept':'text/html'},
        {'User-Agent':'Linux PC/Firefox browser: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1','Accept':'text/html'},
        {'User-Agent':'Chrome OS/Chrome browser: Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36','Accept':'text/html'} 
    ]

# Proxy configuration
proxy = 'http://44vi85622ykjj219217:Igxg7NBrYvQsVzo1@52.86.143.71:9989'  # Replace with your proxy details

proxies = {
    'http': proxy,
    'https': proxy
} 


# In[5]:


service = Service(executable_path=webdriver_path)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

keyword_title = input("Enter Job Title: ")
job_location_data = input("Enter location: ")
region = input("Enter region: e.g., (de.indeed.com, in.indeed.com)")

region_url = 'https://{region}/'.format(region=region)
print(region_url)

driver.get(region_url)

jobs = scrape_indeed_jobs(region_url,keyword_title, job_location_data)
if jobs:
    save_to_json(jobs, "indeed_jobs.json")
    print("Data saved to indeed_jobs.json")
else:
    print("No data to save.")
