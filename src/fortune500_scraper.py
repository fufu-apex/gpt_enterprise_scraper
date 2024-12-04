import os
from bs4 import BeautifulSoup
import logging
import re

class Fortune500Scraper:
    def __init__(self):
        self.html_file = "fortune_500.html"
        self.logger = logging.getLogger(__name__)

    def clean_domain(self, url):
        """Clean and standardize domain names."""
        # Remove any http:// or https:// prefix
        url = re.sub(r'https?://', '', url)
        # Remove any trailing slashes
        url = url.rstrip('/')
        # Remove any www. prefix
        url = re.sub(r'^www\.', '', url)
        return url

    def get_companies(self):
        """Reads Fortune 500 companies from the local HTML file."""
        try:
            self.logger.info("Starting Fortune 500 companies parsing from local file")
            
            with open(self.html_file, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
            
            rows = soup.find_all('tr', role='row')
            companies = []
            
            for row in rows:
                # First try to find an anchor tag with href
                website_td = row.find_all('td')[6] if len(row.find_all('td')) > 6 else None
                if website_td:
                    # Check if there's an anchor tag
                    anchor = website_td.find('a')
                    if anchor and anchor.get('href'):
                        website = self.clean_domain(anchor['href'])
                    else:
                        website = self.clean_domain(website_td.text.strip())
                    
                    if website:
                        companies.append(website)
                        self.logger.info(f"Found company website: {website}")
            
            # Remove duplicates while preserving order
            companies = list(dict.fromkeys(companies))
            
            self.logger.info(f"Successfully retrieved {len(companies)} companies")
            return companies
            
        except FileNotFoundError:
            self.logger.error(f"HTML file not found: {self.html_file}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing Fortune 500 companies: {str(e)}")
            raise