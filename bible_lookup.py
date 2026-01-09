
import json
import os

# Structure: language_code -> { book_name -> { chapter_num -> { verse_num -> text } } }
BIBLE_DATA = {}

def load_bible_data(language_code, filename):
    global BIBLE_DATA
    try:
        # Check if file exists to avoid error if running from different cwd
        file_path = f'data/{filename}'
        if not os.path.exists(file_path):
             # Try absolute path based on this file's location if relative fails
             current_dir = os.path.dirname(os.path.abspath(__file__))
             file_path = os.path.join(current_dir, 'data', filename)
             
             if not os.path.exists(file_path):
                 print(f"File not found: {filename}")
                 return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create a lookup: book_name -> chapter_num -> verse_num -> text
        lookup = {}
        for book in data.get('books', []):
            book_name = book.get('name')
            if not book_name: continue
            
            lookup[book_name] = {}
            for chapter in book.get('chapters', []):
                chapter_num = chapter.get('chapter')
                lookup[book_name][chapter_num] = {}
                for verse in chapter.get('verses', []):
                    verse_num = verse.get('verse')
                    lookup[book_name][chapter_num][verse_num] = verse.get('text', '')
        
        BIBLE_DATA[language_code] = lookup
        print(f"Loaded {language_code} Bible data successfully.")
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Load available bibles
load_bible_data('pl', 'polish_bible.json')
load_bible_data('en', 'english_bible.json')

# Source text for reverse lookup: book_code -> chapter -> { 'full_text': str, 'spans': list of (start, end, verse_num) }
SOURCE_BIBLE_DATA = {}

def load_source_data(filename):
    global SOURCE_BIBLE_DATA
    try:
        import xml.etree.ElementTree as ET
        
        file_path = f'data/{filename}'
        if not os.path.exists(file_path):
             current_dir = os.path.dirname(os.path.abspath(__file__))
             file_path = os.path.join(current_dir, 'data', filename)
             
             if not os.path.exists(file_path):
                 print(f"Source file not found: {filename}")
                 return

        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Structure:
        # verses_by_chapter[(book, chapter)] = list of (verse_num, text)
        import collections
        verses_by_chapter = collections.defaultdict(list)
        
        for verse in root.findall("v"):
            book = verse.attrib["b"]
            chapter = int(verse.attrib["c"])
            verse_num = int(verse.attrib["v"])
            text = verse.text if verse.text else ""
            verses_by_chapter[(book, chapter)].append((verse_num, text))

        temp_data = {}
        
        for (book, chapter), verses in verses_by_chapter.items():
            # sorts just in case xml wasn't sorted, though usually it is
            verses.sort(key=lambda x: x[0]) 
            
            full_text = ""
            spans = []
            current_idx = 0
            
            for verse_num, text in verses:
                # Based on create_db.py: chapter_text += f"{text}\n"
                # exact reconstruction involved text + newline
                
                start = current_idx
                snippet = f"{text}\n"
                end = current_idx + len(snippet)
                
                # We map the range [start, end) to this verse_num
                # Note: 'end' includes the newline, which likely won't be matched in search results easily
                # but valid for span checks.
                spans.append((start, end, verse_num))
                
                full_text += snippet
                current_idx = end
            
            if book not in temp_data:
                temp_data[book] = {}
            
            temp_data[book][chapter] = {
                'full_text': full_text,
                'spans': spans
            }
            
        SOURCE_BIBLE_DATA = temp_data
        print(f"Loaded source data from {filename} successfully with offset mapping.")
        
    except Exception as e:
        print(f"Error loading source data {filename}: {e}")

# Load the source XML used for DB creation
load_source_data('engwebp_vpl.xml')

def get_real_verse_nums(book_code, chapter, text_chunk):
    """
    Identifies the actual verse numbers present in a text chunk 
    by finding the chunk's position in the full chapter text.
    """
    if not SOURCE_BIBLE_DATA:
        return []
    
    book_data = SOURCE_BIBLE_DATA.get(book_code)
    if not book_data:
        return []
        
    chapter_data = book_data.get(int(chapter))
    if not chapter_data:
        return []
        
    full_text = chapter_data['full_text']
    spans = chapter_data['spans']
    
    # Clean up chunk just in case newlines or whitespace mismatch slightly at edges
    # But usually Chroma returns exact substring of page_content.
    # Note: TextSplitter might strip things or chunk effectively.
    # We will try to find the text_chunk inside full_text.
    
    # 1. Try exact match
    start_idx = full_text.find(text_chunk)
    
    # 2. If not found, it might be that text_chunk has stripped newlines or slightly different formatting 
    # if the VectorStore modified it. But standard LangChain usually keeps page_content intact.
    # If the user prompt sent 'strip' text, we might have issues.
    
    if start_idx == -1:
        # Fallback: Try stripped version? 
        # Or maybe the chunk is just a part of it. 
        # For now, let's assume it can be found. 
        # If not found, we can try to match the first line of chunk.
         first_line = text_chunk.split('\n')[0].strip()
         start_idx = full_text.find(first_line)
         if start_idx == -1:
             return []
    
    end_idx = start_idx + len(text_chunk)
    
    # Identify verses that overlap with [start_idx, end_idx)
    found_verses = set()
    
    for v_start, v_end, v_num in spans:
        # Check for overlap
        # Overlap exists if max(start_idx, v_start) < min(end_idx, v_end)
        overlap_start = max(start_idx, v_start)
        overlap_end = min(end_idx, v_end)
        
        if overlap_start < overlap_end:
            # We have an overlap. 
            # To be robust, maybe require some significant overlap?
            # Or just any character overlap counts as "part of this verse is in the chunk"
            # Since the user wants to see the translation for the verses shown,
            # any part of the verse implies we should fetch that verse's translation.
            found_verses.add(v_num)
            
    return sorted(list(found_verses))

def get_bible_text(language, book_name, chapter, verse_nums_str):
    lookup = BIBLE_DATA.get(language)
    if not lookup:
        return None
        
    try:
        if not verse_nums_str:
            return None
            
        nums = [int(n) for n in verse_nums_str.split(',') if n.strip()]
        texts = []
        for v_num in nums:
            p_book = lookup.get(book_name)
            if p_book:
                p_chapter = p_book.get(chapter)
                # Handle string/int key diffs if any, though JSON usually ints
                # Based on load_bible_data, keys are ints if json was ints
                if p_chapter:
                    text = p_chapter.get(v_num) # json load might give int keys
                    if not text:
                         # Try str key just in case
                         text = p_chapter.get(str(v_num))
                         
                    if text:
                        texts.append(text)
        
        if texts:
            return " ".join(texts)
    except Exception as e:
        print(f"Error retrieving {language} text: {e}")
        
    return None

