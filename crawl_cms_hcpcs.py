#!/usr/bin/env python3
"""
Deep crawl CMS HCPCS Alpha-Numeric page and download all resources (zip, pdf, etc.)
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
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "lxml"])
    from bs4 import BeautifulSoup

BASE_URL = "https://www.cms.gov"
START_URL = "https://www.cms.gov/medicare/coding-billing/healthcare-common-procedure-system/alpha-numeric"
DOWNLOAD_DIR = "cms.gov"
VISITED_URLS = set()
DOWNLOADED_FILES = set()

# File extensions to download
DOWNLOAD_EXTENSIONS = {'.zip', '.pdf', '.txt', '.csv', '.xlsx', '.xls', '.docx', '.doc', '.xml'}

def create_download_dir():
    """Create download directory if it doesn't exist"""
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")

def get_page(url, retries=3):
    """Fetch a page with retries"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt + 1}/{retries} for {url}")
                time.sleep(2)
            else:
                print(f"  ERROR: Failed to fetch {url}: {e}")
                return None

def find_downloadable_links(soup, base_url):
    """Find all downloadable file links on the page"""
    links = []
    
    # Find all <a> tags with href
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        full_url = urljoin(base_url, href)
        
        # Check if it's a downloadable file
        parsed = urlparse(full_url)
        path = parsed.path.lower()
        
        # Direct file links
        if any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
            links.append(full_url)
        
        # Links that might lead to download pages
        if any(keyword in path for keyword in ['hcpcs', 'alpha-numeric', 'coding']):
            if full_url not in VISITED_URLS:
                links.append(full_url)
    
    # Also check for direct download links in text/scripts
    page_text = str(soup)
    # Find URLs in text that end with file extensions
    url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+\.(zip|pdf|txt|csv|xlsx?|docx?|xml)'
    matches = re.findall(url_pattern, page_text, re.IGNORECASE)
    for match in matches:
        url = match[0] if isinstance(match, tuple) else match
        if url.startswith('http'):
            links.append(url)
    
    return list(set(links))

def download_file(url, filepath):
    """Download a file from URL"""
    if url in DOWNLOADED_FILES:
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
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
    path = parsed.path
    filename = os.path.basename(path)
    
    if not filename or '.' not in filename:
        # Try to get from query params or create a name
        filename = default
        if 'file' in parsed.query.lower():
            filename = parsed.query.split('=')[-1]
    
    # Clean filename
    filename = re.sub(r'[^\w\.-]', '_', filename)
    return filename

def crawl_page(url, depth=0, max_depth=3):
    """Recursively crawl pages to find downloadable files"""
    if depth > max_depth:
        return
    
    if url in VISITED_URLS:
        return
    
    VISITED_URLS.add(url)
    print(f"\n[{depth}] Crawling: {url}")
    
    response = get_page(url)
    if not response:
        return
    
    # Check if it's a direct file download
    content_type = response.headers.get('Content-Type', '').lower()
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS) or 'application/' in content_type or 'pdf' in content_type:
        # It's a file, download it
        filename = get_filename_from_url(url, f"file_{len(DOWNLOADED_FILES)}")
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        download_file(url, filepath)
        return
    
    # It's an HTML page, parse it
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        print(f"  Could not parse HTML for {url}")
        return
    
    # Find all downloadable links
    links = find_downloadable_links(soup, url)
    
    # Process direct file links
    for link in links:
        parsed_link = urlparse(link)
        path_lower = parsed_link.path.lower()
        
        if any(path_lower.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
            # Direct file link
            filename = get_filename_from_url(link)
            # Create subdirectory structure based on URL path
            url_path = parsed_link.path.strip('/')
            if url_path:
                path_parts = url_path.split('/')[:-1]  # Exclude filename
                subdir = os.path.join(DOWNLOAD_DIR, *path_parts)
            else:
                subdir = DOWNLOAD_DIR
            
            filepath = os.path.join(subdir, filename)
            download_file(link, filepath)
            time.sleep(0.5)  # Be polite
    
    # Recursively crawl related pages
    for link in links:
        if link not in VISITED_URLS:
            parsed_link = urlparse(link)
            # Only crawl CMS pages
            if 'cms.gov' in parsed_link.netloc:
                crawl_page(link, depth + 1, max_depth)
                time.sleep(1)  # Be polite between page requests

def main():
    print("=" * 60)
    print("CMS HCPCS Deep Crawler")
    print("=" * 60)
    
    create_download_dir()
    
    print(f"\nStarting crawl from: {START_URL}")
    print(f"Max depth: 3 levels")
    print(f"Download extensions: {', '.join(DOWNLOAD_EXTENSIONS)}")
    print("\n" + "=" * 60)
    
    crawl_page(START_URL, depth=0, max_depth=3)
    
    print("\n" + "=" * 60)
    print("CRAWL COMPLETE")
    print("=" * 60)
    print(f"Pages visited: {len(VISITED_URLS)}")
    print(f"Files downloaded: {len(DOWNLOADED_FILES)}")
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")

if __name__ == '__main__':
    main()

