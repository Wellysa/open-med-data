#!/usr/bin/env python3
"""
Download all LOINC files from the LOINC download page
Requires login credentials
"""

import os
import re
import sys
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "lxml", "requests"])
    from bs4 import BeautifulSoup

BASE_URL = "https://loinc.org"
LOGIN_URL = "https://loinc.org/wp-login.php"
DOWNLOAD_PAGE_URL = "https://loinc.org/file-access/download-id/470626/"
COMPLETE_DOWNLOAD_URL = "https://loinc.org/download/loinc-complete/"
DOWNLOAD_DIR = "loinc"
VISITED_URLS = set()
DOWNLOADED_FILES = set()

# File extensions to download
DOWNLOAD_EXTENSIONS = {'.zip', '.pdf', '.txt', '.csv', '.xlsx', '.xls', '.docx', '.doc', '.xml', '.db', '.sqlite', '.owl', '.rdf'}

# Login credentials
USERNAME = "cze"
PASSWORD = "czeasd33"

def create_download_dir():
    """Create download directory if it doesn't exist"""
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")

def login(session):
    """Login to LOINC website"""
    print(f"\nLogging in as {USERNAME}...")
    
    # First, get the login page to get any required tokens/cookies
    try:
        login_page = session.get(LOGIN_URL, timeout=30)
        login_page.raise_for_status()
        
        # Parse the login page to find form fields
        soup = BeautifulSoup(login_page.content, 'html.parser')
        
        # Find the login form
        form = soup.find('form', {'id': 'loginform'}) or soup.find('form')
        if not form:
            print("  Could not find login form")
            return False
        
        # Prepare login data
        login_data = {
            'log': USERNAME,
            'pwd': PASSWORD,
            'wp-submit': 'Log In',
            'redirect_to': DOWNLOAD_PAGE_URL,
            'testcookie': '1'
        }
        
        # Find any hidden fields (like nonce, etc.)
        for hidden in form.find_all('input', type='hidden'):
            name = hidden.get('name')
            value = hidden.get('value', '')
            if name:
                login_data[name] = value
        
        # Submit login
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': LOGIN_URL,
            'Origin': BASE_URL
        }
        
        response = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30, allow_redirects=True)
        
        # Check if login was successful (usually redirects or shows user menu)
        if 'wp-admin' in response.url or 'file-access' in response.url or USERNAME.lower() in response.text.lower():
            print(f"  ✓ Login successful!")
            return True
        else:
            print(f"  ✗ Login may have failed. Response URL: {response.url}")
            # Save response for debugging
            with open('login_response.html', 'wb') as f:
                f.write(response.content)
            print("  Saved login response to login_response.html for debugging")
            return False
            
    except Exception as e:
        print(f"  ✗ Login error: {e}")
        return False

def get_page(session, url, retries=3):
    """Fetch a page with retries"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = session.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                print(f"  ERROR: Failed to fetch {url}: {e}")
                return None

def find_downloadable_links(soup, base_url):
    """Find all downloadable file links on the page"""
    links = []
    
    # Find all <a> tags with href
    for tag in soup.find_all('a', href=True):
        href = tag.get('href', '')
        if not href:
            continue
            
        full_url = urljoin(base_url, href)
        
        # Check if it's a downloadable file
        parsed = urlparse(full_url)
        path = parsed.path.lower()
        
        # Direct file links
        if any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
            links.append(full_url)
        
        # Links that might lead to download pages
        if any(keyword in path.lower() for keyword in ['download', 'file', 'loinc', 'complete']):
            if full_url not in VISITED_URLS:
                links.append(full_url)
    
    # Also check for direct download links in text/scripts
    page_text = str(soup)
    # Find URLs in text that end with file extensions
    url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+\.(zip|pdf|txt|csv|xlsx?|docx?|xml|db|sqlite|owl|rdf)'
    matches = re.findall(url_pattern, page_text, re.IGNORECASE)
    for match in matches:
        if isinstance(match, tuple):
            continue
        if match.startswith('http'):
            links.append(match)
    
    # Check for download buttons/forms that might trigger downloads
    for form in soup.find_all('form'):
        action = form.get('action', '')
        if action:
            full_action = urljoin(base_url, action)
            if 'download' in full_action.lower():
                links.append(full_action)
    
    return list(set(links))

def download_file(session, url, filepath):
    """Download a file from URL"""
    if url in DOWNLOADED_FILES:
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': BASE_URL
        }
        response = session.get(url, headers=headers, timeout=300, stream=True)
        response.raise_for_status()
        
        # Check if it's actually a file (not HTML)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type and len(response.content) < 10000:
            # Might be a redirect page, skip
            print(f"  ⚠ Skipping (appears to be HTML): {os.path.basename(filepath)}")
            return False
        
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Download file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"  ✓ Downloaded: {os.path.basename(filepath)} ({file_size:,} bytes)")
        DOWNLOADED_FILES.add(url)
        return True
    except Exception as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False

def get_filename_from_url(url, default="file"):
    """Extract filename from URL"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    
    if not filename or filename == '/':
        # Try to get from query parameters or generate
        query_params = parsed.query
        if 'file' in query_params:
            filename = query_params.split('file=')[1].split('&')[0]
        else:
            filename = default
    
    # Clean filename
    filename = re.sub(r'[^\w\.-]', '_', filename)
    if not filename:
        filename = default
    
    return filename

def accept_terms_and_download(session, page_url):
    """Accept terms and conditions and trigger download"""
    print(f"\nAccepting terms and accessing download page...")
    
    response = get_page(session, page_url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the terms acceptance form
    form = soup.find('form')
    if not form:
        print("  No form found on page")
        return []
    
    # Find the checkbox for terms acceptance
    checkbox = soup.find('input', {'type': 'checkbox', 'name': re.compile(r'tc|terms|accept', re.I)})
    if not checkbox:
        checkbox = soup.find('input', {'type': 'checkbox'})
    
    # Prepare form data
    form_data = {}
    
    # Get all form inputs
    for input_tag in form.find_all(['input', 'select', 'textarea']):
        name = input_tag.get('name')
        if not name:
            continue
        
        input_type = input_tag.get('type', '').lower()
        
        if input_type == 'checkbox':
            # Check the terms checkbox
            if 'tc' in name.lower() or 'terms' in name.lower() or 'accept' in name.lower():
                form_data[name] = '1'  # or 'on' or 'true'
            elif input_tag.get('checked'):
                form_data[name] = input_tag.get('value', '1')
        elif input_type == 'radio':
            if input_tag.get('checked'):
                form_data[name] = input_tag.get('value', '')
        elif input_type == 'submit':
            # Get submit button value
            if 'download' in input_tag.get('value', '').lower() or 'submit' in input_tag.get('value', '').lower():
                form_data[name] = input_tag.get('value', '')
        else:
            value = input_tag.get('value', '')
            if value:
                form_data[name] = value
    
    # If no submit button found, try common names
    if not any('submit' in k.lower() or 'download' in k.lower() for k in form_data.keys()):
        # Try to find submit button
        submit_btn = form.find('button', type='submit') or form.find('input', type='submit')
        if submit_btn:
            name = submit_btn.get('name')
            if name:
                form_data[name] = submit_btn.get('value', 'Submit')
    
    # Get form action
    form_action = form.get('action', '')
    if form_action:
        submit_url = urljoin(page_url, form_action)
    else:
        submit_url = page_url
    
    # Submit the form
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': page_url,
        'Origin': BASE_URL,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = session.post(submit_url, data=form_data, headers=headers, timeout=60, allow_redirects=True)
        print(f"  ✓ Form submitted. Response URL: {response.url}")
        
        # Parse the response to find download links
        soup = BeautifulSoup(response.content, 'html.parser')
        links = find_downloadable_links(soup, BASE_URL)
        
        return links
    except Exception as e:
        print(f"  ✗ Error submitting form: {e}")
        return []

def crawl_download_page(session, url):
    """Crawl the download page to find all files"""
    print(f"\nCrawling download page: {url}")
    
    if url in VISITED_URLS:
        return
    
    VISITED_URLS.add(url)
    
    response = get_page(session, url)
    if not response:
        return
    
    # Check if it's a direct file download
    content_type = response.headers.get('Content-Type', '').lower()
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS) or \
       'application/' in content_type or 'pdf' in content_type or \
       'zip' in content_type or 'octet-stream' in content_type:
        # It's a file, download it
        filename = get_filename_from_url(url, f"file_{len(DOWNLOADED_FILES)}")
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        download_file(session, url, filepath)
        return
    
    # It's an HTML page, parse it
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        print(f"  Could not parse HTML for {url}")
        return
    
    # Find all downloadable links
    links = find_downloadable_links(soup, url)
    
    print(f"  Found {len(links)} potential download links")
    
    # Process direct file links
    for link in links:
        parsed_link = urlparse(link)
        path_lower = parsed_link.path.lower()
        
        if any(path_lower.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
            # Direct file link
            filename = get_filename_from_url(link)
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            download_file(session, link, filepath)
            time.sleep(1)  # Be polite
    
    # Also try to accept terms and get download links
    if 'file-access' in url or 'download' in url.lower():
        form_links = accept_terms_and_download(session, url)
        for link in form_links:
            parsed_link = urlparse(link)
            path_lower = parsed_link.path.lower()
            
            if any(path_lower.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
                filename = get_filename_from_url(link)
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                download_file(session, link, filepath)
                time.sleep(1)

def main():
    print("=" * 60)
    print("LOINC Complete File Downloader")
    print("=" * 60)
    
    create_download_dir()
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Login
    if not login(session):
        print("\n⚠ Warning: Login may have failed, but continuing anyway...")
    
    # Wait a bit after login
    time.sleep(2)
    
    # Try the main download page
    print(f"\nAccessing download page: {DOWNLOAD_PAGE_URL}")
    crawl_download_page(session, DOWNLOAD_PAGE_URL)
    
    # Also try the complete download URL
    print(f"\nAccessing complete download page: {COMPLETE_DOWNLOAD_URL}")
    crawl_download_page(session, COMPLETE_DOWNLOAD_URL)
    
    # Try to find and follow any other download links
    print(f"\nSearching for additional download links...")
    
    # Common LOINC download URLs to try
    additional_urls = [
        "https://loinc.org/download/",
        "https://loinc.org/download/loinc-complete/",
        "https://loinc.org/downloads/",
    ]
    
    for url in additional_urls:
        try:
            crawl_download_page(session, url)
            time.sleep(1)
        except Exception as e:
            print(f"  Error accessing {url}: {e}")
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Pages visited: {len(VISITED_URLS)}")
    print(f"Files downloaded: {len(DOWNLOADED_FILES)}")
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")
    
    if DOWNLOADED_FILES:
        print("\nDownloaded files:")
        for url in DOWNLOADED_FILES:
            print(f"  - {url}")

if __name__ == '__main__':
    main()

