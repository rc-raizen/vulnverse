#!/usr/bin/env python3

import argparse
import json
import time
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque

USER_AGENT = "the_crawler/0.1 (learn)"

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

def load_allowlist(scope_file: str | None) -> list[re.Pattern]:
     """
     Load allowlist regex patterns. Blank lines and lines starting with # are ignored"""
     patterns: list [re.Pattern] = []
     if not scope_file:
          return patterns
     p = Path(scope_file)
     if not p.exists():
          raise FileNotFoundError(f"Scope file not found: {scope_file}")
     for line in p.read_text(encoding="utf-8").splitlines():
          s = line.strip()
          if not s or s.startswith('#'):
               continue
          try:
              patterns.append(re.compile(s))
          except re.error as e:
               print(f"Invalid regex in scope file: {s!r} ({e})")
     return patterns

def in_scope(url: str, allowlist: list[re.Pattern]) -> bool:
    """
    Returns true if URL matches any paterns in the allowlist. If list is empty, default policy used.
    """
    if not allowlist:
         return True
    return any(rx.search(url) for rx in allowlist)
     
def crawl(start_url, max_pages=100, delay=0.2, debug=False, allowlist=None):
     if allowlist is None:
          allowlist = []     
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

               # provided scope allowlist filter
               scoped = {l for l in internal if in_scope(l, allowlist)}


               # Record metadata for this page: status + number of internal links found
               results["discovered"].setdefault(path, []).append({
                "status": resp.status_code,
                "links_found": len(scoped)
               })

               # Add all unseen internal links to the queue to crawl later
               for l in scoped:
                    if l not in seen:
                         seen.add(l)
                         q.append(l)
                         if debug:
                              print(f"      ➕ Queued new link (scoped): {l}")

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
        python3 the_crawler.py --target theCruller.com --output crawl_basic.json
    """
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, help="Domain or URL (e.g. theCruller.com or https://theCruller.com)")
    p.add_argument("--output", default="crawl_basic.json", help="Output JSON filename")
    p.add_argument("--max-pages", type=int, default=50, help="Limit number of pages to crawl")
    p.add_argument("--scope-file", help ="Path to allowlist regex file (one patter per line)")
    p.add_argument("--debug", action="store_true", help="Enable debug output for verbose logging")
    args = p.parse_args()

    # If user gave just a domain, prepend https:// automatically
    if args.target.startswith("http"):
        start = args.target
    else:
        start = "https://" + args.target

    allowlist = load_allowlist(args.scope_file)
    # Run the crawl and collect results
    out = crawl(start, max_pages=args.max_pages, delay= 0.2, debug=args.debug, allowlist=allowlist)

    # Save output to a JSON file (pretty-printed for readability)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"[+] saved {args.output}")

# Standard Python entry point
if __name__ == "__main__":
    main()

