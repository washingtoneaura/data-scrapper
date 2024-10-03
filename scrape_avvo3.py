from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Set the path to your EdgeDriver executable
edge_driver_path = 'C:/Users/User/Python/data-scrapping/msedgedriver.exe'

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
    'https://www.avvo.com/expungement-lawyer/al.html',
    # Add more URLs as needed
]

# Initialize a list to hold all attorney data
attorneys = []

# Function to scrape data from a single page
def scrape_attorneys_from_page(soup):
    for attorney in soup.find_all('div', class_='header'):
        # Extracting name
        name = attorney.find('a', class_='gtm-profile-link search-result-lawyer-name').text if attorney.find('a', class_='gtm-profile-link search-result-lawyer-name') else 'N/A'
        
        # Extracting rating and reviews count
        rating = attorney.find('span', class_='review-score').text if attorney.find('span', class_='review-score') else 'N/A'
        reviews_count = attorney.find('span', class_='reviews-countheader review-count').text if attorney.find('span', class_='reviews-countheader review-count') else 'N/A'

        # Extract details section for additional info
        details_section = attorney.find_next('div', class_='body')
        years_licensed = details_section.find('div', class_='license').text if details_section and details_section.find('div', class_='license') else 'N/A'
        firm_name = details_section.find('div', class_='text-muted').text if details_section and details_section.find('div', class_='text-muted') else 'N/A'
        
        # Extract phone number and website from main search results
        phone1 = attorney.find('div', class_='phone-cta')
        phone1 = phone1.find('span', class_='overridable-lawyer-phone-copy').text if phone1 else 'N/A'
        
        website1 = attorney.find('div', class_='website-wrapper').find('a', class_='gtm-tracking-cta v-cta-organic-mobile-website')['href'] if attorney.find('div', class_='website-wrapper') else 'N/A'

        # Prepare data dictionary for current attorney
        attorney_data = {
            'Attorney Name': name,
            'Name of Firm': firm_name,
            'Phone1': phone1,
            'Website1': website1,
            'Email': 'N/A',
            'Licensed Number of Years': years_licensed,
            'Rating': rating,
            'Reviews Count': reviews_count,
            'Phone': 'N/A',
            'Website': 'N/A',
            'State Bars Licensed In': 'N/A',
            'Legal Areas of Expertise': 'N/A',
        }
        
        # Click on the attorney's profile link to get more details
        profile_link = attorney.find('a', class_='gtm-profile-link search-result-lawyer-name')
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
                
                # Update attorney data with additional details
                attorney_data.update({
                    'Website': website,
                    'Phone': phone,
                    'State Bars Licensed In': state_bars,
                    'Legal Areas of Expertise': legal_areas
                })

            except Exception as e:
                print(f"Error retrieving profile details for {name}: {e}")

            # Append the full details of the attorney
            attorneys.append(attorney_data)

            # Go back to the previous page
            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'header')))  # Wait until the previous page is loaded
        else:
            attorneys.append(attorney_data)  # Append basic data if no profile link

# Iterate through each URL
for url in urls:
    while True:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'header')))  # Wait for the page to load

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
df.to_csv('attorneys_data3.csv', index=False)

print('Data scraping complete. Results saved to attorneys_data3.csv.')