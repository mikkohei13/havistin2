from flask import request
import requests
from bs4 import BeautifulSoup

def main():
    title = None
    url = None
    
    if request.method == 'POST':
        url = request.form.get('inat_url')
        if url:
            try:
                # Add headers to mimic a browser request
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the h2 element within #wrapper
                wrapper = soup.find('div', id='wrapper')
                if wrapper:
                    h2_element = wrapper.find('h2')
                    if h2_element:
                        title = h2_element.get_text(strip=True)
                    else:
                        title = "No h2 title found in wrapper"
                else:
                    title = "No wrapper div found"
                    
            except Exception as e:
                title = f"Error scraping page: {str(e)}"
    
    return {
        'title': title,
        'url': url
    }
