import re
from src.vv_crawler.the_crawler import in_scope, load_allowlist

def test_in_scope_patterns():
    allow = [re.compile(r"^https?://(www\.)?theCruller\.com(/.*)?$")]
    assert in_scope("http://theCruller.com/", allow) is True
    assert in_scope("https://www.theCruller.com/a/b", allow) is True
    assert in_scope("https://theCrawler.com/", allow) is False

def test_empty_allowlist_defaults_true():
    assert in_scope("http://theCruller.com/", []) is True

def test_load_allowlist(tmp_path):
    p =tmp_path / "scope.txt"
    p.write_text("""
# comment
^https?://(www\\.)?theCruller\\.com(/.*)?$
                 
""", encoding="utf-8")
    pats = load_allowlist(str(p))
    assert len(pats) == 1
    assert in_scope("https://theCruller.com/x", pats) is True
    assert in_scope("https://theCrawler.com", pats) is False