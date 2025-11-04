#!/usr/bin/env python3
"""
Bare-bones endpoint crawler script 


- Synchronous, single-worker
- Uses requests + BeautifulSoup
- Only follows same-host links
- Outputs a simple JSON file with discovered paths
- Small and readable so you can step through every line

Usage:
    python bare_crawler.py --target samplecorp.com --output crawl_basic.json --max-pages 50
"""

import argparse
import json
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from collections import deque

USER_AGENT = "theCrawler/0.1 (learn)"

def normalize_url(base, href): # takes a base url and a hyperlink and returns a clean url

    if not href:
         return None # ignore invalid links 
    joined = urljoin(base, href)
    p = urlparse(joined)
    
    return p._replace(fragment="").geturl()

def extract_links(html,base):
     
     soup = BeautifulSoup(html, "html.parser")
     links = set()
     for a in soup.find_all('a', href=True):
         u = normalize_url(base, a["href"])
         if u:
              links.add(u)
     return links

def crawl():
     
     return

def main():
     return

if __name__ == "__main__":
     main()

