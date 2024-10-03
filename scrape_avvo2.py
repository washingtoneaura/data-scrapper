from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set the path to your EdgeDriver executable
edge_driver_path = 'C:/Users/User/Python/data-scrapping/msedgedriver.exe'

# Initialize Edge options
edge_options = EdgeOptions()
# Remove the headless option to see the browser
# edge_options.add_argument('--headless')  # Do not use headless mode
edge_options.add_argument('--disable-gpu')  # Disable GPU acceleration
edge_options.add_argument('--window-size=1920,1080')  # Set the window size if needed

# Create Edge service instance
edge_service = EdgeService(executable_path=edge_driver_path)

# Initialize Edge WebDriver
driver = webdriver.Edge(service=edge_service, options=edge_options)

# List of target URLs to scrape
urls = [
    'https://www.avvo.com/expungement-lawyer/al.html',
    #'https://www.avvo.com/expungement-lawyer/az.html',
    #'https://www.avvo.com/expungement-lawyer/ar.html',
    # Add more URLs as needed
]

# Initialize a list to hold all attorney data
attorneys = []

# Function to scrape data from a single page
def scrape_attorneys_from_page(soup):
    for attorney in soup.find_all('div', class_='header'):
        # Extracting name
        name = attorney.find('a', class_='gtm-profile-link search-result-lawyer-name').text if attorney.find('a', class_='gtm-profile-link search-result-lawyer-name') else 'N/A'
        
        # Extracting rating
        rating_element = attorney.find('span', class_='review-score')
        rating = rating_element.text if rating_element else 'N/A'
        
        # Extracting reviews count
        reviews_count_element = attorney.find('span', class_='reviews-countheader review-count')
        reviews_count = reviews_count_element.text if reviews_count_element else 'N/A'

        # Extracting details section for additional info
        details_section = attorney.find_next('div', class_='body')
        if details_section:
            years_licensed = details_section.find('div', class_='license').text if details_section.find('div', class_='license') else 'N/A'
            firm_name = details_section.find('div', class_='text-muted').text if details_section.find('div', class_='text-muted') else 'N/A'
        else:
            years_licensed = firm_name = 'N/A'
            
         # Extract phone number from cta-major
        phone_element1 = attorney.find('a', class_='gtm-tracking-cta v-cta-organic-mobile-phone overridable-lawyer-phone-link')
        phone1 = phone_element1.find('span', class_='overridable-lawyer-phone-copy').text if phone_element1 else 'N/A'
        
        # Extract website from website-wrapper
        website_element1 = attorney.find('div', class_='website-wrapper').find('a', class_='gtm-tracking-cta v-cta-organic-mobile-website') if attorney.find('div', class_='website-wrapper') else None
        website1 = website_element1['href'] if website_element1 else 'N/A'

        # Extracting phone number and website from CTAs
        ctas_section = details_section.find_next('div', class_='ctas ctas-links') if details_section else None
        if ctas_section:
            phone_element = ctas_section.find('a', class_='gtm-tracking-cta v-cta-organic-mobile-phone')
            phone = phone_element.find('span', class_='overridable-lawyer-phone-copy').text if phone_element else 'N/A'
            website_element = ctas_section.find('a', class_='gtm-tracking-cta v-cta-organic-mobile-website')
            website = website_element['href'] if website_element else 'N/A'
        else:
            phone = website = 'N/A'
        
        # Click on the attorney's profile link to get more details
        profile_link = attorney.find('a', class_='gtm-profile-link search-result-lawyer-name')
        if profile_link:
            driver.get(profile_link['href'])
            time.sleep(1)  # Allow time for the profile page to load
            profile_html = driver.page_source
            profile_soup = BeautifulSoup(profile_html, 'html.parser')

            # Extracting state bars and legal areas of expertise
            state_bars = profile_soup.find('span', class_='profile-location').text if profile_soup.find('span', class_='profile-location') else 'N/A'
            legal_areas = profile_soup.find('span', class_='profile-practice-area').text if profile_soup.find('span', class_='profile-practice-area') else 'N/A'

            # Extracting phone number and website from CTAs
            phone_element = profile_soup.find('a', class_='overridable-lawyer-phone-link')
            phone = phone_element.find('span', class_='overridable-lawyer-phone-copy').text if phone_element else 'N/A'
            website_element = profile_soup.find('a', class_='website-ctrl')
            website = website_element['href'] if website_element else 'N/A'
            
            # Append all details to the attorney's list
            attorneys.append({
                'Attorney Name': name,
                'Name of Firm': firm_name,
                'Website': website,
                'Phone': phone,
                'Email': 'N/A',
                'State Bars Licensed In': state_bars,
                'Legal Areas of Expertise': legal_areas,
                'Licensed Number of Years': years_licensed,
                'Rating': rating,
                'Reviews Count': reviews_count
            })

            # Go back to the previous page
            driver.back()
            time.sleep(1)  # Allow time to navigate back
        else:
            attorneys.append({
                'Attorney Name': name,
                'Name of Firm': firm_name,
                'Phone1': phone1,
                'Website1': website1,
                'Website': website,
                'Phone': phone,
                'Email': 'N/A',
                'State Bars Licensed In': state_bars,
                'Legal Areas of Expertise': legal_areas,
                'Licensed Number of Years': years_licensed,
                'Rating': rating,
                'Reviews Count': reviews_count
            })

# Iterate through each URL
for url in urls:
    # Navigate through pagination for each URL
    while True:
        # Navigate to the URL
        driver.get(url)

        # Allow time for the page to load
        time.sleep(1)

        # Get the page source
        html = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Scrape attorneys from the current page
        scrape_attorneys_from_page(soup)

        # Find the pagination section
        pagination = soup.find('nav', class_='pagination')
        next_page_element = pagination.find('a', rel='next') if pagination else None
        if next_page_element:
            # Update the URL to the next page
            url = 'https://www.avvo.com' + next_page_element['href']  # Prepend base URL
        else:
            break  # No next page, exit the loop

# Close the browser
driver.quit()

# Convert to a pandas DataFrame
df = pd.DataFrame(attorneys)

# Save the data to a CSV file
df.to_csv('attorneys_data2.csv', index=False)

print('Data scraping complete. Results saved to attorneys_data2.csv.')