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

def crawl(start_url, max_pages=100, delay=0.2):
     
     """
     breadth first crawler
     """

     parsed = urlparse(start_url)
     base_netloc = parse = parsed.netloc # extract hostname xxx.com

     # deque for BFS crawl
     q = deque([start_url]) # start with the initial url 
     seen = set([start_url]) # track visited urls

     results = {"base": start_url, "discovered": {}}

     pages = 0 # counter for pages 

     while q and pages < max_pages:
          url = q.popleft()

          try:
               resp = requests.get(url, headers= {"User-Agent": USER_AGENT}, timeout=10)
          except Exception as e:
               print (f"[!] fetch error {url}: {e}")
               continue

          pages += 1

          ctype = resp.headers.get("Content-Type", "") 

          path = urlparse(url).path or "/"

          # --- Handle HTML pages ---
          if "html" in ctype:
               # Parse and extract all hyperlinks
               links = extract_links(resp.text, url)

               # Keep only internal (same-host) links — don't crawl external domains
               internal = {l for l in links if urlparse(l).netloc == base_netloc}

               # Record metadata for this page: status + number of internal links found
               results["discovered"].setdefault(path, []).append({
                "status": resp.status_code,
                "links_found": len(internal)
               })

               # Add all unseen internal links to the queue to crawl later
               for l in internal:
                    if l not in seen:
                         seen.add(l)
                         q.append(l)

        # --- Handle non-HTML pages (APIs, images, etc.) ---
          else:
               results["discovered"].setdefault(path, []).append({
                    "status": resp.status_code,
                    "content_type": ctype
               })

          # Be polite: wait a little between requests to avoid overloading servers
          time.sleep(delay)

     # Add a simple summary to the results
     results["summary"] = {"pages_crawled": pages, "max_pages": max_pages}
     return results

# ----------------------------------------------------------
# Entry point / CLI
# ----------------------------------------------------------
def main():
    """
    Handles command-line arguments and runs the crawler.
    Example:
        python3 theCrawler.py --target samplecorp.com --output crawl_basic.json
    """
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, help="Domain or URL (e.g. samplecorp.com or https://samplecorp.com)")
    p.add_argument("--output", default="crawl_basic.json", help="Output JSON filename")
    p.add_argument("--max-pages", type=int, default=50, help="Limit number of pages to crawl")
    args = p.parse_args()

    # If user gave just a domain, prepend https:// automatically
    if args.target.startswith("http"):
        start = args.target
    else:
        start = "https://" + args.target

    # Run the crawl and collect results
    out = crawl(start, max_pages=args.max_pages)

    # Save output to a JSON file (pretty-printed for readability)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"[+] saved {args.output}")

# Standard Python entry point
if __name__ == "__main__":
    main()

