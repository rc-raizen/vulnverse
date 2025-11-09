import types 
from src.vv_crawler.the_crawler import normalize_url, extract_links

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
    assert normalize_url(base, "search?q=tsuna#top") == "https://theCruller.com/shop/search?q=tsuna"

def test_extract_links(): 
    
    base = "https://theCruller.com/path/"

    html = """ 
    <html><body>
    <a href = "/a"> A </a>
    <a href = "b"> B </a>
    <a href = "https://theCruller.com/c#fragout"> C </a>
    <a href = "#local"> Local </a>
    </body></html>
    """

    links = extract_links(html, base)

    expected = {
        "https://theCruller.com/a",
        "https://theCruller.com/path/b",
        "https://theCruller.com/c",
        "https://theCruller.com/path/"

    }

    assert links == expected