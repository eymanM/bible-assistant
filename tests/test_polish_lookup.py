import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bible_lookup import get_bible_text, get_real_verse_nums

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

def test_lookup_loaded():
    text_pl = get_bible_text('pl', "Genesis", 1, "1")
    assert text_pl is not None, "get_bible_text('pl') returned None. Make sure data/bible.db exists."
    
    text_en = get_bible_text('en', "Genesis", 1, "1")
    assert text_en is not None, "get_bible_text('en') returned None. Make sure data/bible.db exists."

def test_genesis_lookup():
    text_pl = get_bible_text('pl', "Genesis", 1, "1")
    assert text_pl is not None
    assert "stworzył" in text_pl, f"PL Genesis 1:1 text mismatch: '{text_pl}'"

def test_formatting():
    res_pl = get_bible_text('pl', "Genesis", 1, "1")
    assert res_pl is not None
    assert "stworzył" in res_pl
    assert not res_pl.strip().startswith("1 "), "Verse number found in PL text"

    res_en = get_bible_text('en', "Genesis", 1, "1")
    assert res_en is not None
    assert "In the beginning" in res_en
    assert not res_en.strip().startswith("1 "), "Verse number found in EN text"

def test_real_verse_nums():
    # Will just test it doesn't crash on standard input
    nums = get_real_verse_nums("GEN", "1", "In the beginning")
    assert isinstance(nums, list)

if __name__ == "__main__":
    test_lookup_loaded()
    test_genesis_lookup()
    test_formatting()
    test_real_verse_nums()
    print("ALL DATA CHECKS PASSED")
