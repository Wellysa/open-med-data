#!/usr/bin/env python3
"""
Download all LOINC files using browser session cookies
"""

import os
import sys
import re
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_URL = "https://loinc.org"
DOWNLOAD_DIR = "loinc"
USERNAME = "cze"
PASSWORD = "czeasd33"

# URLs to download from
DOWNLOAD_URLS = [
    "https://loinc.org/file-access/download-id/470626/",  # Main LOINC 2.81
    "https://loinc.org/downloads/",  # Downloads page
]

def create_download_dir():
    """Create download directory"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")

def login_and_get_session():
    """Login and return session with cookies"""
    session = requests.Session()
    
    print(f"\nLogging in as {USERNAME}...")
    
    # Get login page
    login_url = "https://loinc.org/wp-login.php"
    response = session.get(login_url, timeout=30)
    
    # Parse form
    soup = BeautifulSoup(response.content, 'html.parser')
    form = soup.find('form', {'id': 'loginform'}) or soup.find('form')
    
    if not form:
        print("  Could not find login form")
        return None
    
    # Prepare login data
    login_data = {
        'log': USERNAME,
        'pwd': PASSWORD,
        'wp-submit': 'Log In',
        'redirect_to': 'https://loinc.org/downloads/',
        'testcookie': '1'
    }
    
    # Get hidden fields
    for hidden in form.find_all('input', type='hidden'):
        name = hidden.get('name')
        if name:
            login_data[name] = hidden.get('value', '')
    
    # Submit login
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': login_url,
    }
    
    response = session.post(login_url, data=login_data, headers=headers, timeout=30, allow_redirects=True)
    
    if USERNAME.lower() in response.text.lower() or 'downloads' in response.url:
        print("  ✓ Login successful!")
        return session
    else:
        print("  ✗ Login may have failed")
        return session  # Continue anyway

def download_file(session, url, filename=None):
    """Download a file"""
    if filename is None:
        filename = os.path.basename(url.split('?')[0])
        if not filename or filename == '/':
            filename = f"file_{int(time.time())}"
    
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"  ⚠ Already exists: {filename}")
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': BASE_URL
        }
        
        response = session.get(url, headers=headers, timeout=300, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check if it's HTML (redirect page)
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type and len(response.content) < 50000:
            print(f"  ⚠ Skipping HTML page: {filename}")
            return False
        
        # Download
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"  ✓ Downloaded: {filename} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {filename} - {e}")
        return False

def find_download_links(session, url):
    """Find all download links on a page"""
    print(f"\nScanning: {url}")
    
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = []
        
        # Find all links
        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')
            if not href:
                continue
            
            full_url = urljoin(url, href)
            
            # Check for download links
            text = tag.get_text(strip=True).lower()
            href_lower = href.lower()
            
            # Direct file links
            if any(href_lower.endswith(ext) for ext in ['.zip', '.csv', '.txt', '.xlsx', '.xls', '.pdf', '.db', '.sqlite']):
                links.append((full_url, os.path.basename(href.split('?')[0])))
            
            # Download-related links
            elif any(keyword in text for keyword in ['download', 'loinc', 'file']) or \
                 any(keyword in href_lower for keyword in ['download', 'file-access', 'file_id']):
                if 'file-access' in href_lower or 'download-id' in href_lower:
                    links.append((full_url, None))  # Will need to visit and download
        
        return links
        
    except Exception as e:
        print(f"  ✗ Error scanning {url}: {e}")
        return []

def accept_terms_and_download(session, url):
    """Accept terms and download from file-access page"""
    print(f"\nProcessing file-access page: {url}")
    
    try:
        response = session.get(url, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find form
        form = soup.find('form')
        if not form:
            print("  No form found")
            return []
        
        # Find checkbox
        checkbox = soup.find('input', {'type': 'checkbox', 'name': re.compile(r'tc|terms|accept', re.I)})
        if not checkbox:
            checkbox = soup.find('input', {'type': 'checkbox'})
        
        # Prepare form data
        form_data = {}
        for input_tag in form.find_all(['input', 'select', 'textarea']):
            name = input_tag.get('name')
            if not name:
                continue
            
            input_type = input_tag.get('type', '').lower()
            
            if input_type == 'checkbox':
                if 'tc' in name.lower() or 'terms' in name.lower() or 'accept' in name.lower():
                    form_data[name] = '1'
            elif input_type == 'submit':
                if 'download' in input_tag.get('value', '').lower():
                    form_data[name] = input_tag.get('value', '')
            else:
                value = input_tag.get('value', '')
                if value:
                    form_data[name] = value
        
        # Submit form
        form_action = form.get('action', '')
        submit_url = urljoin(url, form_action) if form_action else url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': url,
        }
        
        response = session.post(submit_url, data=form_data, headers=headers, timeout=60, allow_redirects=True)
        
        # Try to find download link in response
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for direct download links
        download_links = []
        for tag in soup.find_all('a', href=True):
            href = tag.get('href', '')
            full_url = urljoin(response.url, href)
            if any(full_url.lower().endswith(ext) for ext in ['.zip', '.csv', '.txt', '.xlsx', '.xls', '.pdf']):
                filename = os.path.basename(href.split('?')[0])
                download_links.append((full_url, filename))
        
        # Also check if response is a file download
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/' in content_type or 'zip' in content_type or 'octet-stream' in content_type:
            # It's a file!
            filename = f"loinc_file_{int(time.time())}.zip"
            download_links.append((response.url, filename))
        
        return download_links
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def main():
    print("=" * 60)
    print("LOINC Complete Downloader")
    print("=" * 60)
    
    create_download_dir()
    
    # Login
    session = login_and_get_session()
    if not session:
        print("\n⚠ Could not login, exiting")
        return
    
    time.sleep(2)
    
    downloaded = set()
    
    # Process each URL
    for url in DOWNLOAD_URLS:
        # Find links
        links = find_download_links(session, url)
        
        for link_url, filename in links:
            if link_url in downloaded:
                continue
            
            if 'file-access' in link_url or 'download-id' in link_url:
                # Need to accept terms first
                file_links = accept_terms_and_download(session, link_url)
                for file_url, file_name in file_links:
                    if file_url not in downloaded:
                        download_file(session, file_url, file_name)
                        downloaded.add(file_url)
                        time.sleep(1)
            else:
                # Direct download
                download_file(session, link_url, filename)
                downloaded.add(link_url)
                time.sleep(1)
    
    # Also try direct download URLs
    direct_urls = [
        ("https://loinc.org/download/loinc-complete/", "Loinc_2.81.zip"),
    ]
    
    for url, filename in direct_urls:
        if url not in downloaded:
            download_file(session, url, filename)
            downloaded.add(url)
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Files downloaded: {len(downloaded)}")
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")

if __name__ == '__main__':
    main()

