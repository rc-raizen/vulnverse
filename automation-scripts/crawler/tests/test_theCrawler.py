import types
from crawler.theCrawler import normalize_url, extract_links

def test_normalize_url():

    base = "https://theCruller.com/shop/page.html"

    # relative path
    assert normalize_url(base, "../about.html") == "https://theCruller.com/about.html"

    # absolute URL
    assert normalize_url(base, "https://theCruller.com/contact") == "https://theCruller.com/contact"

    # same-page, fragments removed
    assert normalize_url(base, "#quirk") == "https://theCruller.com/shop/page.html"

    # root-relative path
    assert normalize_url(base, "/support") == "https://theCruller.com/support"

    # query preserved, fragment removed
    assert normalize_url(base, "?q=tsuna#top") == "https://theCruller.com/shop/search?q=tsuna"

def test_extract_links(): 
    ()