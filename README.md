# vulnverse the_crawler v1

A basic, endpoint crawler for authorized testing. Created as a skeleton to continuosly improve overtime with feature additions and adjustments. 

## Features

- **URL Normalization** to return a clean url from hyperlinks
- **HTML Page Parser** to find all links and return absolute urls
- **Breadth-First Crawling** to visit pages, extract links and save results
- **JSON output** for easy readability
- Optional **Rate Limiting** for setting max pages 
- **Regex Scope allowlisting** so only matching URLs are crawled

## Usage 
```bash 
python the_crawler.py \
    --target https://theCruller.com \
    --output crawler_basic.json
    --max-pages 3 \
    --scope-file scope_allowlist.txt
```

### Common Flags
- `--target` : URL or domain to crawl (http/https)
- `--output` : JSON file path 
- `--max-pages` : Limit number of pages to crawl
- `--scope-file` : Path to allowlist regex file

## Output 
``` json
{
  "base": "https://theCruller.com",
  "discovered": {
    "/": [
      {
        "status": 200,
        "links_found": 2
      }
    ],
    "/events": [
      {
        "status": 200,
        "links_found": 4
      }
    ],
    "/education": [
      {
        "status": 200,
        "links_found": 7
      }
    ]
},
"summary": {
    "pages_crawled": 3,
    "max_pages": 3
  }
}
```

## Legal
Use **only** with explicit written authorization. Defaults are conservative.