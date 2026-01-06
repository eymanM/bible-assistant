
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

def get_bible_text(language, book_name, chapter, verse_nums_str):
    lookup = BIBLE_DATA.get(language)
    if not lookup:
        return None
        
    try:
        if not verse_nums_str:
            return None
            
        nums = [int(n) for n in verse_nums_str.split(',')]
        texts = []
        for v_num in nums:
            p_book = lookup.get(book_name)
            if p_book:
                p_chapter = p_book.get(chapter)
                if p_chapter:
                    text = p_chapter.get(v_num)
                    if text:
                        texts.append(text)
        
        if texts:
            return " ".join(texts)
    except Exception as e:
        print(f"Error retrieving {language} text: {e}")
        
    return None

