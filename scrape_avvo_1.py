from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# Set the path to your EdgeDriver executable
edge_driver_path = 'C:/Users/Aura/Desktop/data-scrapper/msedgedriver.exe'

# Initialize Edge options
edge_options = EdgeOptions()
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--window-size=1920,1080')

# Create Edge service instance
edge_service = EdgeService(executable_path=edge_driver_path)

# Initialize Edge WebDriver
driver = webdriver.Edge(service=edge_service, options=edge_options)

# List of target URLs to scrape
urls = [
    'https://www.avvo.com/family-lawyer/ak.html',
    'https://www.avvo.com/family-lawyer/al.html',
    'https://www.avvo.com/family-lawyer/az.html',
    'https://www.avvo.com/family-lawyer/ar.html',
    'https://www.avvo.com/family-lawyer/ca.html',
    'https://www.avvo.com/family-lawyer/co.html',
    'https://www.avvo.com/family-lawyer/ct.html',
    'https://www.avvo.com/family-lawyer/de.html',
    'https://www.avvo.com/family-lawyer/dc.html',
    'https://www.avvo.com/family-lawyer/fl.html',
    'https://www.avvo.com/family-lawyer/ga.html',
    'https://www.avvo.com/family-lawyer/hi.html',
    'https://www.avvo.com/family-lawyer/id.html',
    'https://www.avvo.com/family-lawyer/il.html',
    'https://www.avvo.com/family-lawyer/in.html',
    'https://www.avvo.com/family-lawyer/ia.html',
    'https://www.avvo.com/family-lawyer/ks.html',
    'https://www.avvo.com/family-lawyer/ky.html',
    'https://www.avvo.com/family-lawyer/la.html',
    'https://www.avvo.com/family-lawyer/me.html',
    'https://www.avvo.com/family-lawyer/md.html',
    'https://www.avvo.com/family-lawyer/ma.html',
    'https://www.avvo.com/family-lawyer/mi.html',
    'https://www.avvo.com/family-lawyer/mn.html',
    'https://www.avvo.com/family-lawyer/ms.html',
    'https://www.avvo.com/family-lawyer/mo.html',
    'https://www.avvo.com/family-lawyer/mt.html',
    'https://www.avvo.com/family-lawyer/ne.html',
    'https://www.avvo.com/family-lawyer/nv.html',
    'https://www.avvo.com/family-lawyer/nh.html',
    'https://www.avvo.com/family-lawyer/nj.html',
    'https://www.avvo.com/family-lawyer/nm.html',
    'https://www.avvo.com/family-lawyer/ny.html',
    'https://www.avvo.com/family-lawyer/nc.html',
    'https://www.avvo.com/family-lawyer/nd.html',
    'https://www.avvo.com/family-lawyer/oh.html',
    'https://www.avvo.com/family-lawyer/ok.html',
    'https://www.avvo.com/family-lawyer/or.html',
    'https://www.avvo.com/family-lawyer/pa.html',
    'https://www.avvo.com/family-lawyer/ri.html',
    'https://www.avvo.com/family-lawyer/sc.html',
    'https://www.avvo.com/family-lawyer/sd.html',
    'https://www.avvo.com/family-lawyer/tn.html',
    'https://www.avvo.com/family-lawyer/tx.html',
    'https://www.avvo.com/family-lawyer/ut.html',
    'https://www.avvo.com/family-lawyer/vt.html',
    'https://www.avvo.com/family-lawyer/va.html',
    'https://www.avvo.com/family-lawyer/wa.html',
    'https://www.avvo.com/family-lawyer/wv.html',
    'https://www.avvo.com/family-lawyer/wi.html',
    'https://www.avvo.com/family-lawyer/wy.html',
    #Add more URLs as needed
]

# Initialize a list to hold all attorney data
attorneys = []

# Function to scrape data from a single page
def scrape_attorneys_from_page(soup):
    for attorney in soup.find_all('div', class_='precached serp-card organic-card gtm-tracking-container overridable-lawyer-phone'):
        # Extracting name
        header_div = attorney.find('div', class_='header')
        name = header_div.find('a', class_='gtm-profile-link search-result-lawyer-name').text if header_div.find('a', class_='gtm-profile-link search-result-lawyer-name') else 'N/A'
                  
        # Extract the profile URL
        profile_link_element = header_div.find('a', class_='gtm-profile-link search-result-lawyer-name')
        profile_url = profile_link_element['href'] if profile_link_element else 'N/A'

        # Prepend the base URL if necessary
        if profile_url != 'N/A' and not profile_url.startswith('http'):
            profile_url = 'https://www.avvo.com' + profile_url
            
        # Extracting rating and reviews count
        rating = header_div.find('span', class_='review-score').text if header_div.find('span', class_='review-score') else 'N/A'
        reviews_count = header_div.find('span', class_='reviews-countheader review-count').text if header_div.find('span', class_='reviews-countheader review-count') else 'N/A'

        # Extract details section for additional info
        details_section = attorney.find_next('div', class_='body')
        years_licensed = details_section.find('div', class_='license').text if details_section and details_section.find('div', class_='license') else 'N/A'
        years_licensed_text = details_section.find('div', class_='license').text if details_section and details_section.find('div', class_='license') else 'N/A'
        
        # Use regular expression to find the number in years_licensed_text
        years_licensed_number = re.search(r'\d+', years_licensed_text)
        yearsLicensed = years_licensed_number.group(0) if years_licensed_number else 'N/A'

        firm_name = details_section.find('div', class_='text-muted').text if details_section and details_section.find('div', class_='text-muted') else 'N/A'

        # Extract phone number and website from the ctas ctas-links div
        ctas_div = attorney.find('div', class_='ctas ctas-links')
        
        # Update phone1 extraction based on the provided HTML structure
        phone1 = ctas_div.find('span', class_='overridable-lawyer-phone-copy').text if ctas_div and ctas_div.find('span', class_='overridable-lawyer-phone-copy') else 'N/A'

        # Update website1 extraction to get the profile link
        profile_link = ctas_div.find('div', class_='website-wrapper').find('a', class_='gtm-tracking-cta v-cta-organic-mobile-website')
        website1 = profile_link['href'] if profile_link else 'N/A'

        # Prepare data dictionary for current attorney
        attorney_data = {
            'Attorney Name': name,
            'Profile URL': profile_url,
            'Name of Firm': firm_name,
            'Phone1': phone1,
            'Website1': website1,
            'Email': 'N/A',
            'Licensed Number of Years': years_licensed,
            'Licensed Years Only': yearsLicensed,
            'Rating': rating,
            'Reviews Count': reviews_count,
            'Phone': 'N/A',
            'Website': 'N/A',
            'State Bars Licensed In': 'N/A',
            'Legal Areas of Expertise': 'N/A',
        }

        # Only click the profile link if the website1 is not 'N/A'
        if website1 != 'N/A' and profile_url != 'N/A':
            profile_link = header_div.find('a', class_='gtm-profile-link search-result-lawyer-name')
            if profile_link:
                driver.get(profile_link['href'])
                try:
                    # Wait for the profile page to load and for the necessary elements to be present
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'profile-location')))
                    profile_html = driver.page_source
                    profile_soup = BeautifulSoup(profile_html, 'html.parser')

                    # Extracting state bars and legal areas of expertise
                    state_bars = profile_soup.find('span', class_='profile-location').text if profile_soup.find('span', class_='profile-location') else 'N/A'
                    legal_areas = profile_soup.find('span', class_='profile-practice-area').text if profile_soup.find('span', class_='profile-practice-area') else 'N/A'

                    # Extracting phone number and website from CTAs
                    phone = profile_soup.find('a', class_='overridable-lawyer-phone-link')
                    phone = phone.find('span', class_='overridable-lawyer-phone-copy').text if phone else 'N/A'
                    website = profile_soup.find('a', class_='website-ctrl')
                    website = website['href'] if website else 'N/A'

                    # Extracting firm_name2 (second firm name from profile details) 
                    firm_name2 = profile_soup.find('span', class_='contact-firm').text.strip() if profile_soup.find('span', class_='contact-firm') else 'N/A'
                    
                    # Extract practice areas
                    practice_area_names = []
                    profile_sections = profile_soup.find('div', class_='profile-content')
                    if profile_sections:
                        pa_graphic_wrapper = profile_sections.find('div', class_='profile-sections')
                        if pa_graphic_wrapper:
                            practice_areas_list = pa_graphic_wrapper.find('ol', class_='chart-legend-list')
                            
                            if practice_areas_list:
                                for specialty in practice_areas_list.find_all('li', class_='js-specialty'):
                                    try:
                                        practice_area_name = specialty.find('a').find('div').text.strip()
                                        practice_area_names.append(practice_area_name)
                                    except (AttributeError, IndexError) as e:
                                        print(f"Error extracting practice area: {e}")
                                        continue

                    # Join all practice area names into a single string
                    practice_areas_str = ', '.join(practice_area_names) if practice_area_names else 'N/A'

                    # Update attorney data with additional details
                    attorney_data.update({
                        'Website': website,
                        'Phone': phone,
                        'State Bars Licensed In': state_bars,
                        'Legal Areas of Expertise': legal_areas,
                        'Name of Firm2': firm_name2,
                        'Practice Areas from Profile': practice_areas_str
                    })

                except Exception as e:
                    print(f"Error retrieving profile details for {name}: {e}")

                # Append the full details of the attorney
                attorneys.append(attorney_data)

                # Go back to the previous page
                driver.back()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'header')))  # Wait until the previous page is loaded
        else:
            if website1 != 'N/A':  # Append only if website1 is not 'N/A'
                attorneys.append(attorney_data)  # Append basic data if no profile link or website is 'N/A'

# Main scraping loop for each URL
for url in urls:
    while True:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'header')))  # Wait for the page to load
        
        # Random delay to reduce detection risk
        time.sleep(random.uniform(3, 7))

        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Scrape attorneys from the current page
        scrape_attorneys_from_page(soup)

        # Find the pagination section
        pagination = soup.find('nav', class_='pagination')
        next_page_element = pagination.find('a', rel='next') if pagination else None
        if next_page_element:
            url = 'https://www.avvo.com' + next_page_element['href']  # Prepend base URL
        else:
            break  # No next page, exit the loop

# Close the browser
driver.quit()

# Convert to a pandas DataFrame
df = pd.DataFrame(attorneys)

# Save the data to a CSV file
df.to_csv('attorneys_data_1.csv', index=False)

print('Data scraping complete. Results saved to attorneys_data_1.csv.')