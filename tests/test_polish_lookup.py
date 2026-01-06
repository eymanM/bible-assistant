
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# sys.path.append(...) is above

# Mock Document class to avoid dependency issues in this simple test
class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}




try:
    # Need to make sure bible_lookup can find the file.
    # The test is run from project root, so 'data/polish_bible.json' should work.
    from bible_lookup import BIBLE_DATA, get_bible_text
except ImportError as e:
    print(f"Failed to import bible_lookup: {e}")
    sys.exit(1)

def test_lookup_loaded():
    if not BIBLE_DATA.get('pl'):
        print("FAIL: BIBLE_DATA['pl'] is empty. Make sure data/polish_bible.json exists.")
        return False
    if not BIBLE_DATA.get('en'):
        print("FAIL: BIBLE_DATA['en'] is empty. Make sure data/english_bible.json exists.")
        return False
        
    print(f"PASS: BIBLE_DATA loaded with keys: {list(BIBLE_DATA.keys())}")
    return True


def test_genesis_lookup():
    # Genesis 1:1 Polish
    # text: " Na początku Bóg stworzył niebo i ziemię."
    
    try:
        pl_data = BIBLE_DATA.get('pl')
        gen = pl_data.get("Genesis")
        if not gen:
            print("FAIL: Genesis not found in PL lookup")
            return False
            
        chap1 = gen.get(1)
        verse1 = chap1.get(1)
        if "stworzył niebo" not in verse1:
             print(f"FAIL: PL Genesis 1:1 text mismatch: '{verse1}'")
             return False
             
        print(f"PASS: PL Genesis 1:1 found: '{verse1}'")
        return True
    except Exception as e:
        print(f"FAIL: Exception checking Genesis: {e}")
        return False

def test_formatting():
    # Test valid lookup PL
    print("\n--- Testing PL Lookup ---")
    res_pl = get_bible_text('pl', "Genesis", 1, "1")
    print(f"Lookup PL Genesis 1:1: {res_pl}")
    
    if not res_pl or "stworzył" not in res_pl:
        print("FAIL: PL Genesis 1:1 lookup failed or text mismatch")
        return False
        
    if res_pl.strip().startswith("1 "):
        print("FAIL: Verse number found in PL text")
        return False

    # Test valid lookup EN
    print("\n--- Testing EN Lookup ---")
    res_en = get_bible_text('en', "Genesis", 1, "1")
    print(f"Lookup EN Genesis 1:1: {res_en}")
    
    if not res_en or "In the beginning" not in res_en:
         print("FAIL: EN Genesis 1:1 lookup failed or text mismatch")
         # Check if KJV is different? KJV: "In the beginning God created the heaven and the earth."
         return False
         
    if res_en.strip().startswith("1 "):
        print("FAIL: Verse number found in EN text")
        return False
        
    print("PASS: get_bible_text logic works for both languages")
    return True



if __name__ == "__main__":
    print("Running tests...")
    if test_lookup_loaded() and test_genesis_lookup() and test_formatting():
        print("\nALL DATA CHECKS PASSED")
    else:
        print("\nSOME CHECKS FAILED")
