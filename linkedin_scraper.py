from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import time

def scrape_linkedin():
    '''
    LinkedIn's URL Pattern:

    https://www.linkedin.com/jobs/search?
        keywords=Data           -> Insert query here
        &location=Worldwide     -> Location
        &locationId=            -> Leave it blank
        &geoId=92000000         -> GeoID of??
        &f_TPR=&f_E=2%2C1%2C3   -> Work type (Remote/Hybrid/Onsite) and Experience Level
        &position=1             
        &pageNum=0              

    '''

    # Ask for User input
    u_input = input('Enter Job Search: ')
    content = pd.DataFrame(columns=['job_title', 'company', 'location', 'compensation', 'desc', 'Seniority level', 'Employment type', 'Job function', 'Industries'])

    # Initialize the driver instance
    driver = webdriver.Edge()
    driver.get(f'https://www.linkedin.com/jobs/search?keywords={u_input}&location=Worldwide&locationId=&geoId=92000000&f_TPR=r604800&position=1&pageNum=0')
    driver.maximize_window()
    # driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(2)

    # Scroll down to the bottom of the page to load all JavaScript
    for pause in range(15):
        try:
            show_more_jobs = driver.find_element(By.CLASS_NAME, 'infinite-scroller__show-more-button')
            show_more_jobs.click()
        except Exception:  
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        finally:
            time.sleep(3)

    # Scraping time
    # Select and click all job cards to show the details on the right side
    job_list = driver.find_elements(By.XPATH, '//*[@id="main-content"]/section[2]/ul/li') 

    for n, job in enumerate(job_list):
        job.find_element(By.TAG_NAME, 'a').click()
        time.sleep(1.5)

    # Click the show more button. If uninteractable, just do nothing.
    # This step scrapes all data on the job card and details section
        try:
            driver.find_element(By.CLASS_NAME, 'show-more-less-html__button').click()
        except Exception:
            pass
        finally:
            job_header = job.text       # ---> contains title, company and location
            job_desc = driver.find_element(By.CLASS_NAME, 'description').text
            others = driver.find_elements(By.CLASS_NAME, 'description__job-criteria-item')

            other_details = ''
            for li in others:
                other_details += li.text + '\n'

    # Check if compensation is available then print details
        try:
            compensation = driver.find_element(By.CLASS_NAME, 'salary').text
        except Exception:
            compensation = 'N/A'
        finally:
            content = process_data(content, job_header, compensation, job_desc, other_details)
            

    # Export result to CSV
    print(f'{len(job_list)} total \'{u_input}\' jobs scraped from LinkedIn')
    content.to_csv(f'{int(round(time.time(), 0))}.csv')
       
def process_data(df, header, comp, desc, others):
    try:
        header = header.rstrip().splitlines()
        title = header[0]
        company = header[1]
        loc = header[2]
    except Exception:
        title = company = loc = 'N/A'

    # Just plug in the compensation:
    
    # Process the other details section:
    others = others.rstrip().splitlines()
    keys = [k for k in others[::2]]
    vals = [v for v in others[1::2]]
    others_dict = {k:v for k, v in zip(keys, vals)}

    # Process the description:
    desc = desc.splitlines()
    try:
        cut_index = desc.index('Show less')
        desc = desc[:cut_index]
    except Exception: 
        pass
    finally:
        desc = ' '.join(desc)

    # Collate results in a single dict
    row = {'job_title': title, 'company': company, 'location': loc, 'compensation': comp, 'desc': desc} | others_dict

    # update and return the original dataframe to account for multiple loops.
    final = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    return(final)


if __name__ == "__main__":
    scrape_linkedin()